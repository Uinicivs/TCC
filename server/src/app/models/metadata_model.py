from enum import Enum
from typing import Any
from pydantic import BaseModel


class InputType(str, Enum):
    NUMBER = 'number'
    TEXT = 'text'
    BOOL = 'bool'
    OBJECT = 'object'
    LIST = 'list'


class InputMedata(BaseModel):
    displayName: str
    type: InputType
    required: bool


class StartMetadata(BaseModel):
    inputs: list[InputMedata]


class ConditionalOperationType(str, Enum):
    EQUALS = '=='
    DIFFS = '!='
    GTHAN = '>'
    GETHAN = '>='
    LTHAN = '<'
    LETHAN = '<='


class ConditionalMetadata(BaseModel):
    expression: str


class EndMetadata(BaseModel):
    response: Any
