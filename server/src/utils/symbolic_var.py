from typing import Callable
from z3 import Real, Bool, String, ExprRef, ModelRef, IntNumRef, RatNumRef, BoolRef  # type: ignore

from src.app.models.metadata_model import InputType, StartMetadata


type_mapping: dict[InputType, Callable[[str], ExprRef]] = {
    InputType.BOOL: Bool,
    InputType.NUMBER: Real,
    InputType.TEXT: String,
    InputType.OBJECT: String,
    InputType.LIST: String
}


def symbolic_var_factory(spec: StartMetadata) -> dict[str, ExprRef]:
    return {
        inp.displayName: type_mapping[inp.type](inp.displayName)
        for inp in spec.inputs
    }


def concretize_model(model: ModelRef, vars: dict[str, ExprRef]) -> dict[str, object]:
    def _extract(val):
        if val is None:
            return None
        if isinstance(val, IntNumRef):
            return int(val.as_long())
        if isinstance(val, RatNumRef):
            num = val.numerator_as_long()
            den = val.denominator_as_long()
            return num / den if den != 1 else num
        if isinstance(val, BoolRef):
            return bool(val)
        try:
            return val.as_string()
        except Exception:
            return str(val)

    result = {}
    for name, var in vars.items():
        try:
            if var in model:
                val = model[var]
            else:
                val = model.eval(var, model_completion=True)
            result[name] = _extract(val)
        except Exception:
            result[name] = None
    return result
