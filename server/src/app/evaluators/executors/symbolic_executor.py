# src/app/evaluators/executors/symbolic_executor.py
import hashlib
from typing import Optional, List, Tuple, Set
from z3 import (   # type: ignore
    sat,
    unsat,
    is_le,
    is_lt,
    is_ge,
    is_gt,
    is_or,
    is_and,
    is_not,
    unknown,
    simplify,

    Or,
    Not,
    And,
    Solver,
    BoolVal,
    ExprRef,
    ModelRef,
)

from src.app.evaluators.parser import get_parser
from src.app.evaluators.transformers import SymbolicTransfomer
from src.app.models.node_model import AnyNode, ConditionalNode, EndNode
from src.utils.symbolic_var import symbolic_var_factory, concretize_model
from src.app.core.exceptions import InvalidFlowException, RuntimeException
from src.app.models.symbolic_model import (
    Coverage,
    CaseResult,
    PrunedBranch,
    ReductionInfo,
    SymbolicReport,
)


def _canonical_key_from_exprs(exprs: List[Optional[ExprRef]]) -> str:
    items = sorted(str(e) for e in exprs if e is not None)
    key_text = "|".join(items)
    return hashlib.sha256(key_text.encode("utf-8")).hexdigest()


def expr_to_zf_string(expr: ExprRef) -> str:
    """Converte uma expressão Z3 para uma string legível na sintaxe ZF."""
    if is_and(expr):
        return " and ".join(expr_to_zf_string(c) for c in expr.children())

    if is_or(expr):
        return " or ".join(expr_to_zf_string(c) for c in expr.children())

    if is_not(expr):
        inner = expr.children()[0]
        # tenta detectar negações de comparadores e inverter para sintaxe ZF legível
        if is_le(inner):
            a, b = inner.children()
            return f"{expr_to_zf_string(a)} > {expr_to_zf_string(b)}"
        if is_lt(inner):
            a, b = inner.children()
            return f"{expr_to_zf_string(a)} >= {expr_to_zf_string(b)}"
        if is_ge(inner):
            a, b = inner.children()
            return f"{expr_to_zf_string(a)} < {expr_to_zf_string(b)}"
        if is_gt(inner):
            a, b = inner.children()
            return f"{expr_to_zf_string(a)} <= {expr_to_zf_string(b)}"
        if is_not(inner):
            return expr_to_zf_string(inner.children()[0])
        # fallback
        return f"not ({expr_to_zf_string(inner)})"

    # Caso base: variável, número, comparação simples, função Z3
    s = str(expr)
    s = s.replace("==", "=")
    s = s.replace("And", "and").replace("Or", "or")
    s = s.replace("If", "if")
    return s


class SymbolicExecutor:
    def __init__(self, nodes: List[AnyNode]):
        self.nodes = nodes
        self.solver = Solver()
        self.parser = get_parser()
        self.symbolic_vars = self._create_symbolic_vars()
        self.transformer = SymbolicTransfomer(self.symbolic_vars)

        # aux (outputs)
        self.cases: List[CaseResult] = []
        self.pruned: List[PrunedBranch] = []
        self.conflicts: List[List[str]] = []
        self.duplicates: List[List[str]] = []
        self.reductions: List[ReductionInfo] = []
        # store exprRef lists for every case (for precise analysis later)
        self._case_exprs: List[List[Optional[ExprRef]]] = []

    # -------------------------
    # helpers
    # -------------------------
    def _create_symbolic_vars(self) -> dict[str, ExprRef]:
        start_node = next(
            (node for node in self.nodes if node.nodeType == "START"), None)
        if not start_node:
            raise InvalidFlowException("flow is broken, has no start node")
        return symbolic_var_factory(start_node.metadata)

    def _get_children(self, node_id: str, is_false_case: Optional[bool] = None) -> List[AnyNode]:
        children = [node for node in self.nodes if node.parentNodeId == node_id]
        if is_false_case is not None:
            children = [c for c in children if c.isFalseCase == is_false_case]
        return children

    def _zf_text(self, expr: Optional[ExprRef]) -> str:
        """Retorna representação ZF legível para ExprRef (usa reverse_map se disponível)."""
        if expr is None:
            return "<undecidable>"
        return self.transformer.reverse_map.get(expr, expr_to_zf_string(expr))

    # -------------------------
    # public API
    # -------------------------
    def execute(self) -> SymbolicReport:
        start_node = next(
            (node for node in self.nodes if node.nodeType == "START"), None)
        if not start_node:
            raise InvalidFlowException("flow is broken, has no start node")

        # reset state
        self.cases = []
        self.pruned = []
        self.conflicts = []
        self.duplicates = []
        self.reductions = []
        self._case_exprs = []

        # traversal
        self._traverse(start_node, [])

        # post-analyses
        self._analyze_duplicates()
        self._analyze_conflicts()

        coverage = self._calculate_coverage()
        return SymbolicReport(
            cases=self.cases,
            coverage=coverage,
            pruned=self.pruned,
            # conflicts=self.conflicts,
            reductions=self.reductions,
            # duplicates=self.duplicates,
        )

    # -------------------------
    # traversal
    # -------------------------
    def _traverse(self, node: AnyNode, constraints: List[Optional[ExprRef]]) -> None:
        match node.nodeType:
            case 'START':
                for child in self._get_children(node.nodeId):
                    self._traverse(child, constraints)
                return

            case 'CONDITIONAL':
                assert isinstance(node, ConditionalNode)
                expr_text = getattr(node.metadata, "expression", "").replace(
                    "'", '"').strip()
                try:
                    tree = self.parser.parse(expr_text)
                    cond = self.transformer.transform(tree)
                except Exception as e:
                    raise RuntimeException(
                        f"expression - {expr_text} - from node {node.nodeId} could not be translated: {e}")

                # Simplify w/ context
                simplified_cond, removed_parts = self._simplify_with_context(
                    cond, constraints)
                if removed_parts:
                    self.reductions.append(
                        ReductionInfo(
                            nodeId=node.nodeId,
                            original=self._zf_text(cond),
                            simplified=self._zf_text(simplified_cond),
                            removedParts=[self._zf_text(
                                r) for r in removed_parts]
                        )
                    )

                # True branch (follow only true-children)
                true_cond = simplified_cond
                self._evaluate_branch(
                    node, true_cond, constraints, is_false_case=False)

                # False branch (safe: if simplified_cond is None, treat not_cond as None)
                not_cond = None if simplified_cond is None else Not(
                    simplified_cond)
                self._evaluate_branch(
                    node, not_cond, constraints, is_false_case=True)
                return

            case 'END':
                self._finalize_case(node, constraints)
                return

            case _:
                # Unknown node types: traverse children normally
                for child in self._get_children(node.nodeId):
                    self._traverse(child, constraints)

    # -------------------------
    # simplify w/ context
    # -------------------------
    def _simplify_with_context(self, expr: ExprRef,
                               constraints: List[Optional[ExprRef]]) -> Tuple[ExprRef, List[ExprRef]]:
        # quick path: no context
        if not constraints:
            simplified = simplify(expr)
            # record reverse_map for simplified if missing
            if simplified not in self.transformer.reverse_map:
                self.transformer.reverse_map[simplified] = str(simplified)
            return simplified, []

        # prepare concrete base constraints
        base = [c for c in constraints if c is not None]

        # 0) If base already implies expr -> expr redundant
        s_imp = Solver()
        for c in base:
            s_imp.add(c)
        s_imp.add(Not(expr))
        if s_imp.check() == unsat:
            # expr is implied by context -> redundant
            true_expr = BoolVal(True)
            # register friendly ZF text for this new expr so _zf_text prints "true"
            self.transformer.reverse_map[true_expr] = "true"
            return true_expr, [expr]  # removed_parts contains original expr

        # Otherwise, fall back to previous logic (remove redundant subparts)
        self.solver.push()
        try:
            for c in base:
                self.solver.add(c)

            removed_parts: List[ExprRef] = []

            def remove_redundant_parts(e: ExprRef) -> ExprRef:
                if is_and(e):
                    new_children = []
                    for child in e.children():
                        self.solver.push()
                        self.solver.add(Not(child))
                        try:
                            chk = self.solver.check()
                        finally:
                            self.solver.pop()
                        if chk == unsat:
                            removed_parts.append(child)
                        else:
                            new_children.append(child)
                    if not new_children:
                        return e
                    elif len(new_children) == 1:
                        return new_children[0]
                    else:
                        return And(*new_children)
                elif is_or(e):
                    new_children = []
                    for child in e.children():
                        self.solver.push()
                        self.solver.add(child)
                        try:
                            chk = self.solver.check()
                        finally:
                            self.solver.pop()
                        if chk == unsat:
                            removed_parts.append(child)
                        else:
                            new_children.append(child)
                    if not new_children:
                        return e
                    elif len(new_children) == 1:
                        return new_children[0]
                    else:
                        return Or(*new_children)
                else:
                    return e

            simplified_expr = remove_redundant_parts(expr)
            simplified_expr = simplify(simplified_expr)

            # ensure we have reverse_map entry for the simplified expr (friendly text fallback)
            if simplified_expr not in self.transformer.reverse_map:
                # try to map to a nicer ZF-like string — prefer expr_to_zf_string
                try:
                    pretty = expr_to_zf_string(simplified_expr)
                except Exception:
                    pretty = str(simplified_expr)
                self.transformer.reverse_map[simplified_expr] = pretty

            return simplified_expr, removed_parts
        finally:
            self.solver.pop()

    # -------------------------
    # branch evaluation (with improved prune classification)
    # -------------------------

    def _evaluate_branch(self, node: AnyNode, cond: Optional[ExprRef],
                         constraints: List[Optional[ExprRef]], is_false_case: bool) -> None:
        """
        cond may be None (undecidable). If None, we conservatively don't add it but still explore.
        """
        # If cond is None, we should not call Not(cond) earlier; here cond may be None.
        self.solver.push()
        try:
            # add existing constraints
            for c in constraints:
                if c is not None:
                    self.solver.add(c)

            # add the branch condition if present
            if cond is not None:
                self.solver.add(cond)

            chk = self.solver.check()
            if chk == sat:
                new_constraints = list(constraints) + [cond]
                for child in self._get_children(node.nodeId, is_false_case):
                    self._traverse(child, new_constraints)
            elif chk == unknown:
                child = self._get_children(
                    node.nodeId,
                    is_false_case=is_false_case
                )[0]

                unsat_constraints = [
                    self._zf_text(c) for c in constraints
                    if c is not None
                ]
                if cond is not None:
                    unsat_constraints.append(self._zf_text(cond))

                self.pruned.append(PrunedBranch(
                    nodeId=child.nodeId,
                    isFalseCase=is_false_case,
                    reason="unknown (solver returned unknown)",
                    unsatConstraints=unsat_constraints
                ))
            else:  # unsat
                child = self._get_children(
                    node.nodeId,
                    is_false_case=is_false_case
                )[0]

                unsat_constraints = [
                    self._zf_text(c) for c in constraints
                    if c is not None
                ]
                if cond is not None:
                    unsat_constraints.append(self._zf_text(cond))

                reason = self._classify_pruned_case(constraints, cond)
                self.pruned.append(PrunedBranch(
                    nodeId=child.nodeId,
                    isFalseCase=is_false_case,
                    reason=reason,
                    unsatConstraints=unsat_constraints
                ))
        finally:
            self.solver.pop()

    # -------------------------
    # classify pruned
    # -------------------------
    def _classify_pruned_case(self, constraints: List[Optional[ExprRef]], new_cond: Optional[ExprRef]) -> str:
        """
        Distinguish:
          - 'redundant_condition' if new_cond is implied by constraints
          - 'unreachable' if constraints are sat but constraints + new_cond is unsat
          - 'unsatisfiable' otherwise
        Uses fresh solvers to avoid touching main solver state.
        """
        # Build list of concrete constraints (skip None)
        base = [c for c in constraints if c is not None]

        # If new_cond is None, we can't classify semantically -> mark 'unsatisfiable'
        if new_cond is None:
            return "unsatisfiable"

        # 1) check base satisfiability
        s_base = Solver()
        for c in base:
            s_base.add(c)
        base_sat = s_base.check() == sat

        # 2) check base + new_cond satisfiability
        s_new = Solver()
        for c in base:
            s_new.add(c)
        s_new.add(new_cond)
        new_sat = s_new.check() == sat

        # unreachable: base sat, base + new_cond unsat
        if base_sat and not new_sat:
            return "unreachable"

        # redundant: base implies new_cond -> base ∧ ¬new_cond unsat
        s_imp = Solver()
        for c in base:
            s_imp.add(c)
        s_imp.add(Not(new_cond))
        if s_imp.check() == unsat:
            return "redundant_condition"

        # default
        return "unsatisfiable"

    # -------------------------
    # finalize case
    # -------------------------
    def _finalize_case(self, node: AnyNode, constraints: List[Optional[ExprRef]]) -> None:
        self.solver.push()
        try:
            for c in constraints:
                if c is not None:
                    self.solver.add(c)

            if self.solver.check() == sat:
                model: ModelRef = self.solver.model()
                concrete = concretize_model(model, self.symbolic_vars)
            else:
                concrete = None

            # textualize then dedupe preserving order
            texts = [self._zf_text(c) for c in constraints if c is not None]
            seen = set()
            constraint_texts = []
            for t in texts:
                if t not in seen:
                    seen.add(t)
                    constraint_texts.append(t)

            assert isinstance(node, EndNode)
            self.cases.append(CaseResult(
                endNodeId=node.nodeId,
                endMetadata=node.metadata,
                constraints=constraint_texts,
                concrete=concrete
            ))

            # store expr refs aligned with cases for precise analysis
            self._case_exprs.append(list(constraints))
        finally:
            self.solver.pop()

    # -------------------------
    # duplicates & conflicts
    # -------------------------
    def _analyze_duplicates(self) -> None:
        key_map: dict[str, set[str]] = {}
        for idx, exprs in enumerate(self._case_exprs):
            key = _canonical_key_from_exprs(exprs)
            key_map.setdefault(key, set()).add(self.cases[idx].endNodeId)
        self.duplicates = [sorted(list(v))
                           for v in key_map.values() if len(v) > 1]

    def _analyze_conflicts(self) -> None:
        conflicts_set: Set[Tuple[str, str]] = set()
        N = len(self._case_exprs)
        for i in range(N):
            for j in range(i + 1, N):
                id_a = self.cases[i].endNodeId
                id_b = self.cases[j].endNodeId
                if id_a == id_b:
                    continue
                self.solver.push()
                try:
                    for c in self._case_exprs[i]:
                        if c is not None:
                            self.solver.add(c)
                    for c in self._case_exprs[j]:
                        if c is not None:
                            self.solver.add(c)
                    chk = self.solver.check()
                    if chk == sat:
                        pair = (id_a, id_b) if id_a <= id_b else (id_b, id_a)
                        conflicts_set.add(pair)
                finally:
                    self.solver.pop()
        self.conflicts = [list(pair) for pair in sorted(conflicts_set)]

    # -------------------------
    # coverage
    # -------------------------
    def _calculate_coverage(self) -> Coverage:
        total_end_nodes = len([n for n in self.nodes if n.nodeType == "END"])
        covered_ends = len(
            {case.endNodeId for case in self.cases if case.concrete is not None})
        return Coverage(endCount=covered_ends, totalEndNodes=total_end_nodes)
