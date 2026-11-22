from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class MCPToolOut(BaseModel):
    id: UUID
    name: str
    description: str
    input_schema: Dict[str, Any]
    is_enabled: bool
    requires_approval: bool

    class Config:
        from_attributes = True


class MCPServerOut(BaseModel):
    id: UUID
    name: str
    transport: str
    endpoint_or_command: str
    version: str
    is_active: bool
    health_status: str
    last_connected_at: Optional[datetime] = None
    error_message: Optional[str] = None
    tools: List[MCPToolOut] = []

    class Config:
        from_attributes = True


class MCPToolInvokeRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


class MCPExecutionLogOut(BaseModel):
    id: UUID
    mcp_server_id: UUID
    tool_name: str
    invoked_by_name: Optional[str] = None
    status: str
    duration_ms: float
    created_at: datetime

    class Config:
        from_attributes = True
