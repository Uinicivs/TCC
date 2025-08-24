from pydantic import BaseModel
from typing import Literal
from src.app.models.metadata import StartMetadata, ConditionalMetadata, EndMetadata


class BaseNode(BaseModel):
    nodeId: str
    nodeName: str
    parentNodeId: str | None
    isFalseCase: bool | None


class StartNode(BaseNode):
    nodeType: Literal['START']
    metadata: StartMetadata


class ConditionalNode(BaseNode):
    nodeType: Literal['CONDITIONAL']
    metadata: ConditionalMetadata


class EndNode(BaseNode):
    nodeType: Literal['END']
    metadata: EndMetadata
