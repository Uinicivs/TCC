from pydantic import BaseModel
from typing import Literal, Union
from src.app.models.metadata_model import StartMetadata, ConditionalMetadata, EndMetadata


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


AnyNode = Union[StartNode, ConditionalNode, EndNode]
