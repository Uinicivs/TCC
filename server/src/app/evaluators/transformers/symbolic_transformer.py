from typing import Literal
from lark import Transformer, v_args, Token
from z3 import (   # type: ignore
    And, Or, Not,
    ExprRef, RealVal, StringVal, BoolVal,
    Contains, Length, PrefixOf, SuffixOf, If
)


@v_args(inline=True)
class SymbolicTransfomer(Transformer):
    def __init__(self, symbolic_vars: dict[str, ExprRef]):
        super().__init__()
        self.symbolic_vars = symbolic_vars
        self.reverse_map: dict[ExprRef, str] = {}  # 🔹 Z3 → ZF

    # -------------------------------------------------
    # Helpers para registrar expressões
    # -------------------------------------------------
    def _record(self, expr: ExprRef, text: str) -> ExprRef:
        """Guarda o texto ZF correspondente à expressão simbólica."""
        self.reverse_map[expr] = text
        return expr

    def _collect_children(self, expr: ExprRef, type: Literal['and', 'or']) -> list:
        try:
            if hasattr(expr, 'decl') and expr.decl().name() == type:
                flat = []
                for ch in expr.children():
                    flat.extend(self._collect_children(ch, type))

                return flat
        except Exception:
            pass

        return [expr]

    # --- LITERALS ---
    def number(self, tok: Token):
        expr = RealVal(float(tok.value))
        return self._record(expr, tok.value)

    def string(self, tok: Token):
        text = tok.value
        expr = StringVal(text[1:-1])
        return self._record(expr, text)

    def true(self):
        expr = BoolVal(True)
        return self._record(expr, "true")

    def false(self):
        expr = BoolVal(False)
        return self._record(expr, "false")

    def null(self):
        expr = StringVal("")
        return self._record(expr, "null")

    # --- NAME ACCESS ---
    def name_access(self, first_name: Token, *rest_names):
        full_path = first_name.value
        if rest_names:
            full_path += "_" + "_".join(tok.value for tok in rest_names)

        if full_path not in self.symbolic_vars:
            raise NameError(f"Symbol {full_path} not found in symbolic vars")

        expr = self.symbolic_vars[full_path]
        return self._record(expr, full_path)

    # --- LOGIC OPS ---
    def and_op(self, a, b):
        children = []
        children.extend(self._collect_children(a, 'and'))
        children.extend(self._collect_children(b, 'and'))

        expr = And(*children) if len(children) > 1 else children[0]

        parts = [self.reverse_map.get(ch, str(ch)) for ch in children]
        text = f'({' and '.join(parts)})' if len(parts) > 1 else parts[0]

        return self._record(expr, text)

    def or_op(self, a, b):
        children = []
        children.extend(self._collect_children(a, 'or'))
        children.extend(self._collect_children(b, ))

        expr = Or(*children) if len(children) > 1 else children[0]

        parts = [self.reverse_map.get(ch, str(ch)) for ch in children]
        text = f'({' or '.join(parts)})' if len(parts) > 1 else parts[0]

        return self._record(expr, text)

    def not_op(self, a):
        expr = Not(a)
        text = f"not ({self.reverse_map.get(a, str(a))})"
        return self._record(expr, text)

    # --- COMPARATORS ---
    def compare(self, left, op_node, right):
        op = op_node.data

        mapping = {
            "eq": "=",
            "ne": "!=",
            "lt": "<",
            "le": "<=",
            "gt": ">",
            "ge": ">=",
            "in_op": "in"
        }

        op_text = mapping.get(op, op)
        expr_text = f"{self.reverse_map.get(left, str(left))} {op_text} {self.reverse_map.get(right, str(right))}"

        if op == "eq":
            expr = left == right
        elif op == "ne":
            expr = left != right
        elif op == "lt":
            expr = left < right
        elif op == "le":
            expr = left <= right
        elif op == "gt":
            expr = left > right
        elif op == "ge":
            expr = left >= right
        elif op == "in_op":
            expr = Contains(right, left)
        else:
            raise RuntimeError(f"Unknown comparison operator '{op}'")

        return self._record(expr, expr_text)

    # --- MATH ---
    def add(self, a, b):
        expr = a + b
        text = f"{self.reverse_map.get(a, str(a))} + {self.reverse_map.get(b, str(b))}"
        return self._record(expr, text)

    def sub(self, a, b):
        expr = a - b
        text = f"{self.reverse_map.get(a, str(a))} - {self.reverse_map.get(b, str(b))}"
        return self._record(expr, text)

    def mul(self, a, b):
        expr = a * b
        text = f"{self.reverse_map.get(a, str(a))} * {self.reverse_map.get(b, str(b))}"
        return self._record(expr, text)

    def div(self, a, b):
        expr = a / b
        text = f"{self.reverse_map.get(a, str(a))} / {self.reverse_map.get(b, str(b))}"
        return self._record(expr, text)

    def neg(self, a):
        expr = -a
        text = f"-({self.reverse_map.get(a, str(a))})"
        return self._record(expr, text)

    # --- BUILT-IN'S ---
    def func_call(self, name_tok: Token, *args):
        fname = name_tok.value.lower()
        zf_args = [self.reverse_map.get(a, str(a)) for a in args]

        if fname == "length":
            expr = Length(args[0])
            return self._record(expr, f"length({zf_args[0]})")

        if fname == "contains":
            expr = Contains(args[0], args[1])
            return self._record(expr, f"contains({zf_args[0]}, {zf_args[1]})")

        if fname == "startswith":
            expr = PrefixOf(args[1], args[0])
            return self._record(expr, f"startswith({zf_args[0]}, {zf_args[1]})")

        if fname == "endswith":
            expr = SuffixOf(args[1], args[0])
            return self._record(expr, f"endswith({zf_args[0]}, {zf_args[1]})")

        if fname in ("upper", "lower"):
            raise NotImplementedError(
                f"Built-in '{fname}' not supported symbolically.")

        if fname == "coalesce":
            a, b = args
            expr = If(a == StringVal(""), b, a)
            return self._record(expr, f"coalesce({zf_args[0]}, {zf_args[1]})")

        raise NameError(
            f"Unsupported built-in '{fname}' in symbolic transformer.")

    # --- ENTRYPOINT ---
    def start(self, v):
        return v
