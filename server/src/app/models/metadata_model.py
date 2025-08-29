from pydantic import BaseModel
from typing import Any
from enum import Enum


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
