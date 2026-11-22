from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class SLAPolicy(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sla_policies"

    name = Column(String(150), nullable=False)
    bureau_id = Column(UUID(as_uuid=True), ForeignKey("bureaus.id", ondelete="CASCADE"), nullable=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("complaint_categories.id", ondelete="CASCADE"), nullable=True, index=True)
    priority = Column(String(50), default="Medium", nullable=False)
    resolution_days = Column(Integer, default=30, nullable=False)
    warning_threshold_days = Column(Integer, default=25, nullable=False)
    escalation_level = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class SLAEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sla_events"

    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("sla_policies.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False)  # Warning, Breach, Escalated
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    remarks = Column(Text, nullable=True)
