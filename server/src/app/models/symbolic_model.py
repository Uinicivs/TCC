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
    is_false_case: bool
    reason: str


class ReductionInfo(BaseModel):
    nodeId: str
    original: str
    simplified: str
    removed_parts: list[str]


class Coverage(BaseModel):
    end_count: int
    total_end_nodes: int


class SymbolicReport(BaseModel):
    cases: list[CaseResult]
    pruned: list[PrunedBranch]
    duplicates: list[list[str]]
    conflicts: list[list[str]]
    reductions: list[ReductionInfo]
    coverage: Coverage
