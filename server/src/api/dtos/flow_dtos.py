from pydantic import BaseModel
from typing import Optional
from src.app.models.flow import Flow


class CreateFlowInDTO(BaseModel):
    flowName: str
    flowDescription: str


class UpdateFlowInDTO(BaseModel):
    flowName: Optional[str]
    flowDescription: Optional[str]


class ReadFlowOutDTO(Flow):
    pass
