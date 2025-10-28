from datetime import datetime, timezone
from typing import List, Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator

from src.app.models.node_model import AnyNode


PyObjectId = Annotated[str, BeforeValidator(str)]


class Flow(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    flowId: Optional[PyObjectId] = Field(
        alias='_id',
        default=None,
        serialization_alias='flowId'
    )
    flowName: str
    flowDescription: str
    ownerId: PyObjectId
    nodes: List[AnyNode] = []
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
