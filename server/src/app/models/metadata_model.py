from enum import Enum
from typing import Any
from pydantic import BaseModel


class InputType(str, Enum):
    NUMBER = 'number'
    TEXT = 'text'
    BOOL = 'bool'


class InputMetadata(BaseModel):
    displayName: str
    type: InputType
    required: bool


class StartMetadata(BaseModel):
    inputs: list[InputMetadata]


class ConditionalMetadata(BaseModel):
    expression: str


class EndMetadata(BaseModel):
    response: Any
