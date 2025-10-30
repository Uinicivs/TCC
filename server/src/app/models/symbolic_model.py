from pydantic import BaseModel
from typing import Optional, Any

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


class SymbolicReport(BaseModel):
    cases: list[CaseResult]
    pruned: list[PrunedBranch]
    # duplicates: list[list[str]]
    # conflicts: list[list[str]]
    reductions: list[ReductionInfo]
    coverage: Coverage
