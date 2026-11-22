from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class InstitutionAliasOut(BaseModel):
    id: UUID
    alias_name: str
    alias_type: str

    class Config:
        from_attributes = True


class InstitutionIdentifierOut(BaseModel):
    id: UUID
    identifier_type: str
    identifier_value: str

    class Config:
        from_attributes = True


class InstitutionCreate(BaseModel):
    aicte_permanent_id: str = Field(..., description="Official AICTE Permanent ID, e.g. 1-1234567890")
    name: str = Field(..., min_length=3, max_length=300)
    alternate_names: Optional[List[str]] = []
    institution_type: str = "Private"
    address: str
    city: str
    district: str
    state: str
    pincode: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    regional_office_id: Optional[UUID] = None
    approval_status: str = "Approved"


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    alternate_names: Optional[List[str]] = None
    institution_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    regional_office_id: Optional[UUID] = None
    approval_status: Optional[str] = None
    is_active: Optional[bool] = None


class InstitutionOut(BaseModel):
    id: UUID
    aicte_permanent_id: str
    name: str
    alternate_names: Optional[List[str]] = None
    institution_type: str
    address: str
    city: str
    district: str
    state: str
    pincode: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    regional_office_id: Optional[UUID] = None
    regional_office_name: Optional[str] = None
    approval_status: str
    is_verified: bool
    is_active: bool
    complaint_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime
    aliases: List[InstitutionAliasOut] = []
    identifiers: List[InstitutionIdentifierOut] = []

    class Config:
        from_attributes = True


class InstitutionListResponse(BaseModel):
    items: List[InstitutionOut]
    total: int
    page: int
    limit: int
    pages: int
