from pydantic import BaseModel
from typing import List
from enum import Enum


class InputType(str, Enum):
    NUMBER = 'number'
    TEXT = 'text'
    BOOL = 'bool'


class InputMedata(BaseModel):
    displayName: str
    type: InputType
    required: bool


class StartMetadata(BaseModel):
    inputs: List[InputMedata]


class ConditionalOperationType(str, Enum):
    EQUALS = '=='
    DIFFS = '!='
    GTHAN = '>'
    GETHAN = '>='
    LTHAN = '<'
    LETHAN = '<='


class ConditionalMetadata(BaseModel):
    variable: str
    operation: ConditionalOperationType
    value: None | str | float | bool


class EndMetadata(BaseModel):
    response: None | str | float | bool
