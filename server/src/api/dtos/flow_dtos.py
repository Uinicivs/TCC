from pydantic import BaseModel, Field
from typing import Optional, List
from src.app.models.flow_model import Flow, AnyNode


class CreateFlowInDTO(BaseModel):
    flowName: str
    flowDescription: str


class UpdateFlowInDTO(BaseModel):
    flowName: Optional[str] = None
    flowDescription: Optional[str] = None


class ReadFlowOutDTO(Flow):
    pass


class ReadFlowsOutDTO(Flow):
    nodes: List[AnyNode] = Field(exclude=True)


UpdateNodesInDTO = AnyNode
