from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class MCPServer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mcp_servers"

    name = Column(String(150), unique=True, nullable=False, index=True)
    transport = Column(String(50), default="stdio", nullable=False)  # stdio, http
    endpoint_or_command = Column(String(300), nullable=False)
    version = Column(String(50), default="1.0.0", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    health_status = Column(String(50), default="HEALTHY", nullable=False)
    last_connected_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    tools = relationship("MCPTool", back_populates="server", cascade="all, delete-orphan")
    execution_logs = relationship("MCPExecutionLog", back_populates="server", cascade="all, delete-orphan")


class MCPTool(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mcp_tools"

    mcp_server_id = Column(UUID(as_uuid=True), ForeignKey("mcp_servers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    input_schema = Column(JSONB, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)

    # Relationships
    server = relationship("MCPServer", back_populates="tools")


class MCPExecutionLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mcp_execution_logs"

    mcp_server_id = Column(UUID(as_uuid=True), ForeignKey("mcp_servers.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False, index=True)
    invoked_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    input_arguments = Column(JSONB, nullable=False)
    output_payload = Column(JSONB, nullable=True)
    status = Column(String(50), default="SUCCESS", nullable=False)  # SUCCESS, ERROR, PENDING_APPROVAL
    duration_ms = Column(Float, default=0.0, nullable=False)

    # Relationships
    server = relationship("MCPServer", back_populates="execution_logs")

