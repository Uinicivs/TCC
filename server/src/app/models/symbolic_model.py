from datetime import datetime, timezone
from typing import Optional, Any, Annotated
from pydantic import Field, BaseModel, ConfigDict, BeforeValidator

from src.app.models.metadata_model import EndMetadata


class CaseResult(BaseModel):
    endNodeId: str
    endMetadata: EndMetadata
    constraints: list[str]
    concrete: Optional[dict[str, Any]]


class PrunedBranch(BaseModel):
    nodeId: str
    isFalseCase: bool
    reason: str
    unsatConstraints: Optional[list[str]] = None


class ReductionInfo(BaseModel):
    nodeId: str
    original: str
    simplified: str
    removedParts: list[str]


class Coverage(BaseModel):
    endCount: int
    totalEndNodes: int


class UncoveredPath(BaseModel):
    nodeId: str
    constraints: list[str]


class SymbolicReport(BaseModel):
    cases: list[CaseResult]
    pruned: list[PrunedBranch]
    reductions: list[ReductionInfo]
    uncovered: list[UncoveredPath]
    coverage: Coverage


PyObjectId = Annotated[str, BeforeValidator(str)]


class SymbolicExecution(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    id: Optional[PyObjectId] = Field(
        alias='_id',
        default=None,
        serialization_alias='id'
    )
    flowId: PyObjectId
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    pruned: int
    reductions: int
    uncovered: int
    coverage: float
