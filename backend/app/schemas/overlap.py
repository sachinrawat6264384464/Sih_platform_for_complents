from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class OverlapStageBreakdown(BaseModel):
    exact_id: float
    name_fuzzy: float
    geo_proximity: float
    category_match: float
    bm25_text: float
    vector_similarity: float
    cross_bureau: float


class OverlapCandidateOut(BaseModel):
    id: UUID
    complaint_a_id: UUID
    complaint_a_number: str
    complaint_a_title: str
    complaint_a_bureau: str
    complaint_b_id: UUID
    complaint_b_number: str
    complaint_b_title: str
    complaint_b_bureau: str
    institution_id: UUID
    institution_name: str
    aicte_permanent_id: str
    total_confidence_score: float
    stage_scores: OverlapStageBreakdown
    match_reasons: List[str]
    status: str  # Pending, Confirmed, False_Positive, Linked
    created_at: datetime

    class Config:
        from_attributes = True


class OverlapReviewRequest(BaseModel):
    verdict: str = Field(..., description="Confirmed, False_Positive, Linked")
    remarks: str = Field(..., min_length=5, description="Officer justification for overlap decision")


class OverlapCandidateListResponse(BaseModel):
    items: List[OverlapCandidateOut]
    total: int
    pending_count: int
    confirmed_count: int

