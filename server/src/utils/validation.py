from typing import Any, Union
from pydantic import create_model

from src.app.models.metadata_model import InputType, StartMetadata


type_mapping = {
    InputType.BOOL: bool,
    InputType.NUMBER: float,
    InputType.TEXT: str,
    InputType.OBJECT: dict[str, Union[str, float, bool]],
    InputType.LIST: list
}


def _get_pydantic_type(type: InputType, required: bool) -> Any:
    field_type = type_mapping[type]

    return field_type if required else Union[field_type, None]


def create_dynamic_model(spec: StartMetadata) -> type:
    fields: dict[str, Any] = {}

    for f_spec in spec.inputs:
        fields[f_spec.displayName] = (
            _get_pydantic_type(f_spec.type, f_spec.required),
            ... if f_spec.required else None
        )

    return create_model('DynamicSpec', **fields)
