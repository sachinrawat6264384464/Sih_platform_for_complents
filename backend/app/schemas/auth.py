from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class PermissionOut(BaseModel):
    id: UUID
    code: str
    name: str
    module: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleOut(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    permissions: List[PermissionOut] = []

    class Config:
        from_attributes = True


class BureauAssignmentOut(BaseModel):
    id: UUID
    bureau_id: Optional[UUID] = None
    bureau_name: Optional[str] = None
    bureau_code: Optional[str] = None
    regional_office_id: Optional[UUID] = None
    regional_office_name: Optional[str] = None
    is_primary: bool
    role_title: Optional[str] = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[datetime] = None
    roles: List[str] = []
    permissions: List[str] = []
    bureau_assignments: List[BureauAssignmentOut] = []

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    role_codes: List[str] = ["CASE_OFFICER"]
    bureau_id: Optional[UUID] = None
    regional_office_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    is_active: Optional[bool] = None
    role_codes: Optional[List[str]] = None
    password: Optional[str] = None
