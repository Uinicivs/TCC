from pydantic import BaseModel, Field, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from typing import List, Union
from datetime import datetime
from bson import ObjectId
from src.models.node import StartNode, ConditionalNode, EndNode


class PyObjectId(ObjectId):
    """Compatibilidade com Pydantic v2."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(ObjectId)
            ])
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


AnyNode = Union[StartNode, ConditionalNode, EndNode]


class Flow(BaseModel):
    flowId: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    flowName: str
    flowDescription: str
    createdAt: datetime
    updatedAt: datetime
    nodes: List[AnyNode]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
