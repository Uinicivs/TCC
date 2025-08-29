from pydantic import BaseModel, RootModel, Field
from typing import Optional, List, Dict, Any
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


class EvaluateFlowPayloadDTO(RootModel):
    root: Dict[str, Any]

    def __getitem__(self, key):
        try:
            return self.root[key]
        except KeyError:
            return None


class EvaluateFlowResponseDTO(BaseModel):
    response: Any
