from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, ASSIGN, TRANSFER, LOGIN, APPROVE
    entity_type = Column(String(50), nullable=False, index=True)  # INSTITUTION, COMPLAINT, CASE, USER, INTEGRATION
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    changes = Column(JSONB, nullable=True)  # { "before": {...}, "after": {...} }
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class SecurityEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "security_events"

    event_type = Column(String(100), nullable=False, index=True)  # FAILED_LOGIN, UNAUTHORIZED_ACCESS, RATE_LIMIT, FORBIDDEN
    ip_address = Column(String(50), nullable=True)
    details = Column(JSONB, nullable=False)


class SystemSetting(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "system_settings"

    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)

