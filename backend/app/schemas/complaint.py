from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.complaint import ComplaintPriority, ComplaintStatus


class CategoryOut(BaseModel):
    id: UUID
    code: str
    name: str
    severity_level: str
    default_sla_days: int

    class Config:
        from_attributes = True


class SourceSystemOut(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class ComplaintCreate(BaseModel):
    institution_id: UUID
    bureau_id: UUID
    source_system_id: Optional[UUID] = None
    category_id: UUID
    title: str = Field(..., min_length=5, max_length=300)
    description: str = Field(..., min_length=10)
    complainant_type: str = "Citizen"
    complainant_name: Optional[str] = None
    complainant_email: Optional[str] = None
    complainant_phone: Optional[str] = None
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    due_date: Optional[datetime] = None


class ComplaintUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    priority: Optional[ComplaintPriority] = None
    due_date: Optional[datetime] = None


class StatusTransitionRequest(BaseModel):
    new_status: ComplaintStatus
    remarks: str = Field(..., min_length=3, description="Mandatory remarks explaining the status change")
    reason: Optional[str] = None


class ComplaintOut(BaseModel):
    id: UUID
    complaint_number: str
    institution_id: UUID
    institution_name: Optional[str] = None
    aicte_permanent_id: Optional[str] = None
    bureau_id: UUID
    bureau_name: Optional[str] = None
    bureau_code: Optional[str] = None
    source_system_id: UUID
    source_system_name: Optional[str] = None
    category_id: UUID
    category_name: Optional[str] = None
    title: str
    description: str
    complainant_type: str
    complainant_name: Optional[str] = None
    status: ComplaintStatus
    priority: ComplaintPriority
    received_date: datetime
    due_date: Optional[datetime] = None
    disposed_date: Optional[datetime] = None
    is_overlapping: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplaintListResponse(BaseModel):
    items: List[ComplaintOut]
    total: int
    page: int
    limit: int
    pages: int

