from typing import Optional, List, Tuple
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

    Not,
    And,
    Solver,
    BoolVal,
    ExprRef,
    ModelRef,
    CheckSatResult,
)

from src.app.core.config import get_settings
from src.app.evaluators.parser import get_parser
from src.app.evaluators.transformers import SymbolicTransfomer
from src.app.models.node_model import AnyNode, ConditionalNode, EndNode
from src.utils.symbolic_var import symbolic_var_factory, concretize_model
from src.app.core.exceptions import (
    RuntimeException,
    InvalidFlowException,
    SymbolicTimeoutException,
)
from src.app.models.symbolic_model import (
    Coverage,
    CaseResult,
    PrunedBranch,
    UncoveredPath,
    ReductionInfo,
    SymbolicReport,
)


settings = get_settings()


def expr_to_zf_string(expr: ExprRef) -> str:
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
    s = s.replace("And", "and").replace("Or", "or").replace("Not", "not")
    return s


class SymbolicExecutor:
    def __init__(self, nodes: List[AnyNode]):
        self.nodes = nodes

        self.solver = Solver()
        self.solver.set(
            'timeout',
            settings.Z3_SOLVER_TIMEOUT_MILLISECONDS
        )

        self.simplifier_solver = Solver()

        self.parser = get_parser()
        self.symbolic_vars = self._create_symbolic_vars()
        self.transformer = SymbolicTransfomer(self.symbolic_vars)
        self.transformer.reverse_map[BoolVal(True)] = "true"

        # aux (outputs)
        self.cases: List[CaseResult] = []
        self.pruned: List[PrunedBranch] = []
        self.uncovered: List[UncoveredPath] = []
        self.reductions: List[ReductionInfo] = []
        # store exprRef lists for every case (for precise analysis later)
        self._case_exprs: List[List[Optional[ExprRef]]] = []

    # -------------------------
    # helpers
    # -------------------------
    def _reset_simplifier(self):
        try:
            self.simplifier_solver.reset()
        finally:
            self.simplifier_solver.set(
                "timeout",
                settings.Z3_SOLVER_TIMEOUT_MILLISECONDS
            )

    def _check_with_timeout(self, solver: Solver) -> CheckSatResult:
        res = solver.check()
        if res == unknown:
            reason = solver.reason_unknown()
            if "timeout" in reason:
                raise SymbolicTimeoutException()

        return res

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
        if expr is None:
            return "<undecidable>"

        try:
            # attempt to find canonical simplified key in reverse_map
            simp = simplify(expr)
            if simp in self.transformer.reverse_map:
                return self.transformer.reverse_map[simp]
            if expr in self.transformer.reverse_map:
                return self.transformer.reverse_map[expr]
        except Exception:
            pass
        return expr_to_zf_string(expr)

    # -------------------------
    # public API
    # -------------------------
    def execute(self) -> SymbolicReport:
        start_node = next(
            (node for node in self.nodes if node.nodeType == "START"), None)
        if not start_node:
            raise InvalidFlowException("flow is broken, has no start node")

        self.cases.clear()
        self.pruned.clear()
        self.uncovered.clear()
        self.reductions.clear()
        self._case_exprs.clear()

        stack: list[tuple[AnyNode, list[Optional[ExprRef]], Optional[bool]]] = []
        for child in self._get_children(start_node.nodeId):
            stack.append((child, [], None))

        while stack:
            node, constraints, is_false_case = stack.pop()

            if node.nodeType == "CONDITIONAL":
                assert isinstance(node, ConditionalNode)
                expr_text = node.metadata.expression.replace("'", '"').strip()
                try:
                    tree = self.parser.parse(expr_text)
                    cond = self.transformer.transform(tree)
                except Exception as e:
                    raise RuntimeException(
                        f'expression - {expr_text} - from node {node.nodeId} '
                        f'could not be translated: {e}'
                    )

                # attempt to simplify with context
                try:
                    simplified, removed_parts = self._simplify_with_context(
                        cond,
                        [c for c in constraints if c is not None]
                    )
                except SymbolicTimeoutException:
                    raise
                except Exception:
                    # fallback to original cond if simplification fails unexpectedly
                    simplified, removed_parts = cond, []

                if removed_parts:
                    # map removed parts to readable strings
                    removed_texts = [self._zf_text(r) for r in removed_parts]
                    orig_text = self._zf_text(cond)
                    simp_text = self._zf_text(simplified)
                    self.reductions.append(ReductionInfo(
                        nodeId=node.nodeId,
                        original=orig_text,
                        simplified=simp_text,
                        removedParts=removed_texts
                    ))

                # process true branch (is_false_case=False)
                self._process_branch(
                    node, simplified, constraints, stack, False)
                # process false branch (is_false_case=True) using Not(simplified)
                self._process_branch(node, Not(simplified),
                                     constraints, stack, True)

            elif node.nodeType == "END":
                assert isinstance(node, EndNode)
                # finalize case
                self._finalize_case(node, constraints)

        # post-processing
        coverage = self._calculate_coverage()

        return SymbolicReport(
            cases=self.cases,
            coverage=coverage,
            pruned=self.pruned,
            uncovered=self.uncovered,
            reductions=self.reductions,
        )

    # -------------------------
    # core operations
    # -------------------------
    def _process_branch(
        self,
        node: AnyNode,
        cond: Optional[ExprRef],
        constraints: list[Optional[ExprRef]],
        stack: list[tuple[AnyNode, list[Optional[ExprRef]], Optional[bool]]],
        is_false_case: bool,
    ):
        if cond is not None:
            # use a fresh reset of simplifier to check condition in isolation
            self._reset_simplifier()
            try:
                self.simplifier_solver.add(cond)
                chk = self._check_with_timeout(self.simplifier_solver)
                if chk == unsat:
                    # the condition itself is impossible
                    child_nodes = self._get_children(
                        node.nodeId, is_false_case)
                    unsat_constraints = [self._zf_text(cond)]
                    for child in child_nodes:
                        self.pruned.append(PrunedBranch(
                            nodeId=child.nodeId,
                            isFalseCase=is_false_case,
                            reason="unsatisfiable",
                            unsatConstraints=unsat_constraints
                        ))
                    return
            finally:
                # always reset simplifier after this quick check
                self._reset_simplifier()

        # 2) Evaluate condition in the context of accumulated constraints using main solver
        # push/pop to isolate context
        self.solver.push()
        try:
            for c in constraints:
                if c is not None:
                    self.solver.add(c)
            if cond is not None:
                self.solver.add(cond)

            chk = self._check_with_timeout(self.solver)
            if chk == sat:
                new_constraints = list(constraints) + [cond]

                child_nodes = self._get_children(node.nodeId, is_false_case)

                if not child_nodes:
                    if node.nodeType != 'END':
                        self.uncovered.append(
                            UncoveredPath(
                                nodeId=node.nodeId,
                                constraints=[
                                    self._zf_text(c) for c in new_constraints if c is not None
                                ]
                            )
                        )
                    return

                for child in child_nodes:
                    stack.append((child, new_constraints, is_false_case))
            elif chk == unsat:
                # build unsat_constraints (dedupe and preserve order)
                unsat_constraints = []
                seen = set()
                for c in constraints:
                    if c is not None:
                        t = self._zf_text(c)
                        if t not in seen:
                            unsat_constraints.append(t)
                            seen.add(t)
                if cond is not None:
                    t = self._zf_text(cond)
                    if t not in seen:
                        unsat_constraints.append(t)
                        seen.add(t)

                child_nodes = self._get_children(node.nodeId, is_false_case)
                for child in child_nodes:
                    self.pruned.append(PrunedBranch(
                        nodeId=child.nodeId,
                        isFalseCase=is_false_case,
                        reason="unreachable",
                        unsatConstraints=unsat_constraints
                    ))
            else:
                # should not happen because _check_with_timeout raises on unknown
                raise SymbolicTimeoutException()
        finally:
            self.solver.pop()

    def _simplify_with_context(self, expr: ExprRef,
                               base: List[Optional[ExprRef]]) -> Tuple[ExprRef, List[ExprRef]]:
        removed_parts: list[ExprRef] = []

        # normalize base (filter None)
        concrete_base = [c for c in base if c is not None]

        # Helper: check base ∧ candidate is UNSAT (i.e., candidate impossible under base)
        def _base_contradicts(candidate: ExprRef) -> bool:
            try:
                self._reset_simplifier()
                for c in concrete_base:
                    self.simplifier_solver.add(c)
                self.simplifier_solver.add(candidate)
                chk = self._check_with_timeout(self.simplifier_solver)
                return chk == unsat
            finally:
                self._reset_simplifier()

        # Helper: check base implies candidate (base => candidate)
        def _base_implies(candidate: ExprRef) -> bool:
            try:
                self._reset_simplifier()
                for c in concrete_base:
                    self.simplifier_solver.add(c)
                self.simplifier_solver.add(Not(candidate))
                chk = self._check_with_timeout(self.simplifier_solver)
                return chk == unsat
            finally:
                self._reset_simplifier()

        # Helper: check if a => b without relying on base
        def _implies_without_base(a: ExprRef, b: ExprRef) -> bool:
            try:
                self._reset_simplifier()
                self.simplifier_solver.add(a)
                self.simplifier_solver.add(Not(b))
                chk = self._check_with_timeout(self.simplifier_solver)
                return chk == unsat
            finally:
                self._reset_simplifier()

        # 0) If no context, allow only "real" simplify improvements (conservative)
        if not concrete_base:
            if is_and(expr):
                children = list(expr.children())
                remaining = []
                removed_parts = []

                for ch in children:
                    redundant = False
                    for other in children:
                        if ch is other:
                            continue
                        # Se other ⇒ ch, então ch é redundante
                        if _implies_without_base(other, ch):
                            redundant = True
                            break

                    if redundant:
                        removed_parts.append(ch)
                    else:
                        remaining.append(ch)

                if removed_parts:
                    # se tudo foi removido → True
                    if not remaining:
                        true_expr = BoolVal(True)
                        try:
                            self.transformer.reverse_map[simplify(
                                true_expr)] = "true"
                        except Exception:
                            pass
                        return true_expr, removed_parts

                    # se sobra 1 → retorna direto
                    if len(remaining) == 1:
                        new_expr = remaining[0]
                    else:
                        new_expr = And(*remaining)

                    try:
                        self.transformer.reverse_map[simplify(
                            new_expr)] = self._zf_text(new_expr)
                    except Exception:
                        pass

                    return new_expr, removed_parts

            # fallback padrão sem contexto
            try:
                simplified = simplify(expr)
            except Exception:
                return expr, []

            if simplified is None or str(simplified) == str(expr):
                return expr, []

            try:
                is_bool_literal = (
                    simplified.eq(BoolVal(True))
                    or simplified.eq(BoolVal(False))
                )
            except Exception:
                is_bool_literal = False

            if is_bool_literal or len(str(simplified)) < len(str(expr)):
                try:
                    self.transformer.reverse_map[simplified] = self._zf_text(
                        simplified)
                except Exception:
                    pass
                return simplified, [expr]

            return expr, []

        # 1) If base contradicts the whole expr -> this is NOT a reduction, it's a contradiction
        try:
            if _base_contradicts(expr):
                return expr, []
        except SymbolicTimeoutException:
            raise
        except Exception:
            # if simplifier fails unexpectedly, continue with conservative path
            pass

        # 2) If it's a conjunction, test each conjunct individually and remove those implied by base
        try:
            if is_and(expr):
                children = list(expr.children())
                remaining = []

                for ch in children:
                    try:
                        if _base_implies(ch):
                            removed_parts.append(ch)
                        else:
                            # also protect: if base contradicts the child, that's inconsistency (handled elsewhere),
                            # but don't treat as reduction here.
                            remaining.append(ch)
                    except SymbolicTimeoutException:
                        # propagate timeout
                        raise
                    except Exception:
                        # on unexpected errors, keep the child (conservative)
                        remaining.append(ch)

                # if all children removed => expression fully redundant -> True
                if not remaining:
                    true_expr = BoolVal(True)
                    try:
                        self.transformer.reverse_map[simplify(
                            true_expr)] = "true"
                    except Exception:
                        pass
                    return true_expr, removed_parts

                # build new expr
                if len(remaining) == 1:
                    new_expr = remaining[0]
                else:
                    new_expr = And(*remaining)

                if str(new_expr) == str(expr):
                    return expr, []

                # register pretty mapping only if textual form changed
                try:
                    if self._zf_text(new_expr) != self._zf_text(expr):
                        self.transformer.reverse_map[simplify(
                            new_expr)] = self._zf_text(new_expr)
                except Exception:
                    pass

                return new_expr, removed_parts
        except SymbolicTimeoutException:
            raise
        except Exception:
            # fallback to next strategies
            pass

        # 3) Whole-expression implication: if base => expr then expr is redundant
        try:
            if _base_implies(expr):
                true_expr = BoolVal(True)
                try:
                    self.transformer.reverse_map[simplify(true_expr)] = "true"
                except Exception:
                    pass
                return true_expr, [expr]
        except SymbolicTimeoutException:
            raise
        except Exception:
            pass

        # 4) Controlled use of simplify(): accept only real improvements
        try:
            simplified = simplify(expr)
            if simplified is not None and str(simplified) != str(expr):
                try:
                    is_bool_literal = simplified.eq(
                        BoolVal(True)) or simplified.eq(BoolVal(False))
                except Exception:
                    is_bool_literal = False

                if is_bool_literal or len(str(simplified)) < len(str(expr)):
                    try:
                        self.transformer.reverse_map[simplified] = self._zf_text(
                            simplified)
                    except Exception:
                        pass
                    return simplified, [expr]
        except Exception:
            pass

        # 5) Final conservative fallback: try main solver to check base => expr (if simplifier unavailable)
        try:
            self.solver.push()
            for c in concrete_base:
                self.solver.add(c)
            self.solver.add(Not(expr))
            chk2 = self._check_with_timeout(self.solver)
            if chk2 == unsat:
                true_expr = BoolVal(True)
                try:
                    self.transformer.reverse_map[simplify(true_expr)] = "true"
                except Exception:
                    pass
                return true_expr, [expr]
        finally:
            try:
                self.solver.pop()
            except Exception:
                # defensive: if pop fails, raise clearer error upstream
                raise RuntimeException(
                    "Solver stack imbalance during simplify_with_context fallback")

        # nothing changed
        return expr, []

    def _finalize_case(self, node: AnyNode, constraints: List[Optional[ExprRef]]) -> None:
        self.solver.push()
        try:
            for c in constraints:
                if c is not None:
                    self.solver.add(c)

            chk = self._check_with_timeout(self.solver)
            if chk == sat:
                model: ModelRef = self.solver.model()
                concrete = concretize_model(model, self.symbolic_vars)
            else:
                concrete = None

            seen = set()
            constraint_texts = []
            for c in constraints:
                if c is None:
                    continue
                text = self._zf_text(c)
                if text not in seen:
                    seen.add(text)
                    constraint_texts.append(text)

            assert isinstance(node, EndNode)
            self.cases.append(CaseResult(
                endNodeId=node.nodeId,
                endMetadata=node.metadata,
                constraints=constraint_texts,
                concrete=concrete
            ))
            self._case_exprs.append(list(constraints))
        finally:
            self.solver.pop()

    # -------------------------
    # coverage
    # -------------------------
    def _calculate_coverage(self) -> Coverage:
        total_end_nodes = len([n for n in self.nodes if n.nodeType == "END"])
        covered_ends = len(
            {case.endNodeId for case in self.cases if case.concrete is not None})
        return Coverage(endCount=covered_ends, totalEndNodes=total_end_nodes)
