from lark import Transformer, v_args, Token, Tree


@v_args(inline=True)
class ConcreteTransformer(Transformer):
    def __init__(self, env: dict = {}):
        super().__init__()

        self.env = env

        self.buitins = {
            'length': self._builtin_length,
            'substring': self._builtin_substring,
            'upper': self._builtin_upper,
            'lower': self._builtin_lower,
            'contains': self._builtin_contains,
            'startsWith': self._builtin_startswith,
            'endsWith': self._builtin_endswith,
            # lists
            'append': self._builtin_append,
            'remove': self._builtin_remove,
            'count': self._builtin_count,
            # logic / misc
            'is null': self._builtin_is_null,
            'coalesce': self._builtin_coalesce,
        }

    # --- LITERALS ---
    def number(self, tok: Token):
        return float(tok.value)

    def string(self, tok: Token):
        return tok.value[1:-1]

    def true(self):
        return True

    def false(self):
        return False

    def null(self):
        return None

    # --- CONTAINERS ---
    def list_literal(self, *items):
        return list(*items)

    def pair(self, key_tok: Token, value):
        raw = key_tok.value

        if raw.startswith('"') and raw.endswith('"'):
            key = raw[1:-1]
        else:
            key = raw

        return (key, value)

    def context_literal(self, *pairs):
        d = {}

        for k, v in pairs:
            d[k] = v

        return d

    # --- NAME ACCESS AND INDEXING ---
    def name_access(self, first_name: Token, *rest_names):
        name = first_name.value

        if name not in self.env:
            raise NameError(f"Variable '{name}' not found in environment.")

        val = self.env[name]

        for tok in rest_names:
            key = tok.value

            if isinstance(val, dict):
                if key in val:
                    val = val[key]
                else:
                    raise KeyError(
                        f"Key '{key}' not found in nested environment for variable '{name}'.")
            else:
                raise TypeError(
                    f"Expected a dict for key access in variable '{name}', got {type(val).__name__}.")

        return val

    def name_index(self, *parts):
        if len(parts) < 2:
            raise RuntimeError(
                "name_index expects at least a name and an index.")

        *name_tokens, idx = parts

        first = name_tokens[0]
        rest = name_tokens[1:]

        if not isinstance(first, Token):
            raise RuntimeError("First part of name_index must be a Token.")

        name = first.value
        if name not in self.env:
            raise NameError(f"Variable '{name}' not found in environment.")

        val = self.env[name]

        for tok in rest:
            if not isinstance(tok, Token):
                raise RuntimeError(
                    "All parts of name_index after the first must be Tokens.")

            key = tok.value
            if isinstance(val, dict):
                if key in val:
                    val = val[key]
                else:
                    raise KeyError(
                        f"Key '{key}' not found in nested environment for variable '{name}'.")
            else:
                raise TypeError(
                    f"Expected a dict for key access in variable '{name}', got {type(val).__name__}.")

        return self._do_index(val, idx)

    def list_index(self, lst, idx):
        return self._do_index(lst, idx)

    def expr_index(self, expr_val, idx):
        return self._do_index(expr_val, idx)

    def index_access(self, val):
        return val

    def _do_index(self, container, idx):
        if idx is None:
            raise TypeError("Index value is None.")

        if not isinstance(idx, (int, float)):
            raise TypeError(
                f"Index must be int or float, got {type(idx).__name__}.")

        py_idx = int(idx) - 1
        if container is None:
            raise TypeError("Container is None for indexing.")

        if not isinstance(container, (list, tuple, str)):
            raise TypeError(
                f"Container must be list, tuple, or str, got {type(container).__name__}.")

        if py_idx < 0 or py_idx >= len(container):
            raise IndexError(
                f"Index {py_idx+1} out of range for container of length {len(container)}.")

        return container[py_idx]

    # --- FUNC CALLS ---
    def func_call(self, name_tok: Token, *args):
        fname = name_tok.value

        if fname not in self.buitins:
            raise NameError(f"Function '{fname}' is not a built-in.")

        fn = self.buitins[fname]
        if not callable(fn):
            raise TypeError(f"Built-in function '{fname}' is not callable")

        return fn(*args)

    # -- CONDITIONAL | LOGIC ---
    def if_expr(self, cond, then_v, else_v):
        if cond is None:
            raise TypeError("Condition in if_expr is None.")
        if not isinstance(cond, bool):
            raise TypeError(
                f"Condition in if_expr must be bool, got {type(cond).__name__}.")

        return then_v if cond else else_v

    def or_op(self, a, b):
        if not isinstance(a, bool):
            raise TypeError(
                f"First operand of or_op must be bool, got {type(a).__name__}.")

        if a:
            return True

        if not isinstance(b, bool):
            raise TypeError(
                f"Second operand of or_op must be bool, got {type(b).__name__}.")

        return b

    def and_op(self, a, b):
        if not isinstance(a, bool):
            raise TypeError(
                f"First operand of and_op must be bool, got {type(a).__name__}.")

        if not a:
            return False

        if not isinstance(b, bool):
            raise TypeError(
                f"Second operand of and_op must be bool, got {type(b).__name__}.")

        return b

    def not_op(self, a):
        if not isinstance(a, bool):
            raise TypeError(
                f"Operand of not_op must be bool, got {type(a).__name__}.")

        return not a

    # --- COMPARATORS ---
    def compare(self, left, op_node, right):
        op = op_node.data

        if op == 'eq':
            return left == right
        if op == 'ne':
            return left != right

        if left is None or right is None:
            raise TypeError("Cannot compare None values.")

        if op == 'lt':
            return left < right
        if op == 'le':
            return left <= right
        if op == 'gt':
            return left > right
        if op == 'ge':
            return left >= right

        if op == 'in_op' or op == 'in':
            # value in list or string
            return self._do_in_operator(left, right)

        raise RuntimeError("Unknown comparison operator in compare().")

    def eq(self): return Tree('eq', [])
    def ne(self): return Tree('ne', [])
    def lt(self): return Tree('lt', [])
    def le(self): return Tree('le', [])
    def gt(self): return Tree('gt', [])
    def ge(self): return Tree('ge', [])
    def in_op(self): return Tree('in_op', [])

    def _do_in_operator(self, left, right):
        if right is None:
            raise TypeError("Right operand for 'in' operator is None.")

        if isinstance(right, str):
            if not isinstance(left, str):
                raise TypeError(
                    f"Left operand for 'in' with string must be str, got {type(left).__name__}.")
            return left in right

        if isinstance(right, (list, tuple)):
            return left in right

        raise TypeError(
            f"Right operand for 'in' must be str, list, or tuple, got {type(right).__name__}.")

    # --- MATH ---
    def add(self, a, b):
        if a is None or b is None:
            return None

        # numbers
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if isinstance(a, int) and isinstance(b, int):
                return a + b
            return float(a) + float(b)

        # strings
        if isinstance(a, str) and isinstance(b, str):
            return a + b

        # lists
        if isinstance(a, list) and isinstance(b, list):
            return a + b

        raise TypeError(
            "Operands for add must be both numbers, both strings, or both lists.")

    def sub(self, a, b):
        if a is None or b is None:
            return None

        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if isinstance(a, int) and isinstance(b, int):
                return a - b
            return float(a) - float(b)

        raise TypeError("Operands for sub must be both numbers.")

    def mul(self, a, b):
        if a is None or b is None:
            return None

        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if isinstance(a, int) and isinstance(b, int):
                return a * b
            return float(a) * float(b)

        raise TypeError("Operands for mul must be both numbers.")

    def div(self, a, b):
        if a is None or b is None:
            return None

        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError(
                f"Division operands must be numeric. Got {type(a).__name__} and {type(b).__name__}.")
        if b == 0:
            raise ZeroDivisionError("Division by zero")

        return float(a) / float(b)

    def neg(self, a):
        if a is None:
            return None

        if not isinstance(a, (int, float)):
            raise TypeError(
                f"Operand for neg must be numeric. Got {type(a).__name__}.")

        return -a

    # --- BUILT-IN'S ---
    def _builtin_length(self, x):
        if x is None:
            return None

        if isinstance(x, (str, list, tuple)):
            return len(x)

        raise TypeError("_builtin_length expects str, list, or tuple.")

    def _builtin_substring(self, text, start, length=None):
        if text is None or start is None:
            return None

        if not isinstance(text, str):
            raise TypeError(
                f"_builtin_substring expects text as str, got {type(text).__name__}.")
        if not isinstance(start, (int, float)):
            raise TypeError(
                f"_builtin_substring expects start as int or float, got {type(start).__name__}.")

        s = int(start) - 1
        if length is None:
            return text[s:]

        if not isinstance(length, (int, float)):
            raise TypeError(
                f"_builtin_substring expects length as int or float, got {type(length).__name__}.")

        ls = int(length)

        return text[s:s+ls]

    def _builtin_upper(self, s):
        if s is None:
            return None

        if not isinstance(s, str):
            raise TypeError(
                f"_builtin_upper expects str, got {type(s).__name__}.")

        return s.upper()

    def _builtin_lower(self, s):
        if s is None:
            return None

        if not isinstance(s, str):
            raise TypeError(
                f"_builtin_lower expects str, got {type(s).__name__}.")

        return s.lower()

    def _builtin_contains(self, container, item):
        if container is None:
            return None

        # string contains
        if isinstance(container, str):
            if not isinstance(item, str):
                raise TypeError(
                    "_builtin_contains expects item as str when container is str.")
            return item in container

        # list contains
        if isinstance(container, (list, tuple)):
            return item in container

        raise TypeError(
            f"_builtin_contains expects container as str, list, or tuple. Got {type(container).__name__}.")

    def _builtin_startswith(self, s, prefix):
        if s is None or prefix is None:
            return None

        if not isinstance(s, str) or not isinstance(prefix, str):
            raise TypeError(
                "_builtin_startswith expects both s and prefix as str.")

        return s.startswith(prefix)

    def _builtin_endswith(self, s, suffix):
        if s is None or suffix is None:
            return None

        if not isinstance(s, str) or not isinstance(suffix, str):
            raise TypeError(
                "_builtin_endswith expects both s and suffix as str.")

        return s.endswith(suffix)

    # --- LISTS ---
    def _builtin_append(self, lst, value):
        if lst is None:
            return None

        if not isinstance(lst, list):
            raise TypeError(
                f"_builtin_append expects lst as list, got {type(lst).__name__}.")

        return lst + [value]

    def _builtin_remove(self, lst, value):
        if lst is None:
            return None

        if not isinstance(lst, list):
            raise TypeError(
                f"_builtin_remove expects lst as list, got {type(lst).__name__}.")

        new = list(lst)
        try:
            new.remove(value)
        except ValueError:
            pass

        return new

    def _builtin_count(self, x):
        if x is None:
            return None

        if isinstance(x, (list, tuple, str)):
            return len(x)

        return 1

    # --- MISC ---
    def _builtin_is_null(self, x):
        return x is None

    def _builtin_coalesce(self, *args):
        for a in args:
            if a is not None:
                return a

        return None

    # --- START (ENTRYPOINT) ---
    def start(self, v):
        return v
