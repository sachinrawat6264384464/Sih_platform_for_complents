from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    read_at: Optional[datetime] = None
    link_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceOut(BaseModel):
    email_enabled: bool
    in_app_enabled: bool
    sms_enabled: bool
    overlap_alerts: bool
    sla_warnings: bool
    transfer_alerts: bool

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    overlap_alerts: Optional[bool] = None
    sla_warnings: Optional[bool] = None
    transfer_alerts: Optional[bool] = None
