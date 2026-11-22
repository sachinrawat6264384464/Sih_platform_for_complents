from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class IntegrationConfigCreate(BaseModel):
    name: str = Field(..., max_length=150)
    connector_type: str = Field(..., description="PGRC, RB, REGIONAL, EMAIL, CSV_SFTP")
    base_url: Optional[str] = None
    auth_type: str = "API_KEY"
    credentials: Optional[Dict[str, Any]] = None
    sync_frequency_minutes: int = 60
    webhook_secret: Optional[str] = None


class IntegrationConfigUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    auth_type: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    sync_frequency_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None


class IntegrationConfigOut(BaseModel):
    id: UUID
    name: str
    connector_type: str
    base_url: Optional[str] = None
    auth_type: str
    sync_frequency_minutes: int
    is_active: bool
    is_paused: bool
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationSyncRunOut(BaseModel):
    id: UUID
    integration_config_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    records_fetched: int
    records_imported: int
    records_failed: int
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

