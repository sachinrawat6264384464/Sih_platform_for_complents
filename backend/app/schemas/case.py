from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CaseAssignmentCreate(BaseModel):
    officer_id: UUID
    role_description: str = "Lead Investigator"


class CaseActionCreate(BaseModel):
    action_type: str  # Inspection, Show Cause Notice, Hearing, Penalty, Coordination Note
    action_title: str = Field(..., max_length=200)
    action_details: str
    action_date: Optional[datetime] = None


class CaseTransferCreate(BaseModel):
    target_bureau_id: UUID
    reason: str = Field(..., min_length=10)


class CaseTransferReview(BaseModel):
    approved: bool
    decision_remarks: str = Field(..., min_length=5)


class CaseEscalationCreate(BaseModel):
    reason: str = Field(..., min_length=10)
    escalation_level: int = 1
    escalated_to_id: Optional[UUID] = None


class CaseOut(BaseModel):
    id: UUID
    case_number: str
    complaint_id: UUID
    complaint_number: Optional[str] = None
    institution_id: UUID
    institution_name: Optional[str] = None
    aicte_permanent_id: Optional[str] = None
    bureau_id: UUID
    bureau_name: Optional[str] = None
    lead_bureau_id: Optional[UUID] = None
    lead_bureau_name: Optional[str] = None
    title: str
    current_status: str
    coordination_notes: Optional[str] = None
    is_coordinated: bool
    sla_status: str
    expected_disposal_date: Optional[datetime] = None
    assigned_officer_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseStatusHistoryOut(BaseModel):
    id: UUID
    previous_status: Optional[str] = None
    new_status: str
    changed_by_name: Optional[str] = None
    remarks: str
    transition_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    items: List[CaseOut]
    total: int
    page: int
    limit: int
    pages: int

