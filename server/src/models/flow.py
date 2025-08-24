from pydantic import BaseModel
from datetime import datetime
from src.models.node import StartNode, ConditionalNode, EndNode


class Flow(BaseModel):
    flowId: str
    flowName: str
    flowDescription: str
    createdAt: datetime
    updatedAt: datetime
    nodes: StartNode | ConditionalNode | EndNode
