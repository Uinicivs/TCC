from pydantic import BaseModel, Field, ConfigDict, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
from src.app.models.node_model import AnyNode


class PyObjectId(ObjectId):
    """Compatibilidade com Pydantic v2."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetCoreSchemaHandler):
        validation_schema = core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(ObjectId)
            ])
        )

        return core_schema.json_or_python_schema(
            # Usa o mesmo schema para validar dados de JSON ou Python
            json_schema=validation_schema,
            python_schema=validation_schema,

            # AQUI ESTÁ A CORREÇÃO: Define como serializar o objeto
            serialization=core_schema.plain_serializer_function_ser_schema(
                # A função a ser chamada na serialização (str(obj))
                function=str,
                when_used='json'  # Aplica apenas ao serializar para JSON
            )
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v

        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class Flow(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {  # Um exemplo para sua documentação do Swagger
                "flowId": "60d5ec49e7e2d7e3c9a00000",
                "flowName": "Exemplo de Fluxo",
                "flowDescription": "Descrição do fluxo de exemplo.",
                "createdAt": "2025-08-25T10:00:00Z",
                "updatedAt": "2025-08-25T10:00:00Z",
                "nodes": []
            }
        },
    )

    flowId: PyObjectId = Field(
        default_factory=PyObjectId,
        serialization_alias="flowId",
        alias='_id'
    )
    flowName: str
    flowDescription: str
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    nodes: List[AnyNode] = []
