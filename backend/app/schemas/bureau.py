from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class BureauCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    escalation_level: int = 1


class BureauUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    escalation_level: Optional[int] = None


class BureauOut(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    escalation_level: int
    active_cases_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegionalOfficeCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    city: str
    state: str
    jurisdiction_states: Optional[List[str]] = []


class RegionalOfficeUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    jurisdiction_states: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RegionalOfficeOut(BaseModel):
    id: UUID
    code: str
    name: str
    city: str
    state: str
    jurisdiction_states: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

