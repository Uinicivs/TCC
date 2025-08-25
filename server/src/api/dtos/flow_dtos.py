from pydantic import BaseModel
from typing import Optional
from src.app.models.flow_model import Flow, AnyNode


class CreateFlowInDTO(BaseModel):
    flowName: str
    flowDescription: str


class UpdateFlowInDTO(BaseModel):
    flowName: Optional[str] = None
    flowDescription: Optional[str] = None


class ReadFlowOutDTO(Flow):
    pass


UpdateNodesInDTO = AnyNode
