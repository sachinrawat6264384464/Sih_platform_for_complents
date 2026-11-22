from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SecurityEventOut(BaseModel):
    id: UUID
    event_type: str
    ip_address: Optional[str] = None
    details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class SystemSettingOut(BaseModel):
    id: UUID
    setting_key: str
    setting_value: Dict[str, Any]
    description: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
