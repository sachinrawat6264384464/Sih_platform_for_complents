import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ComplaintStatus(str, enum.Enum):
    RECEIVED = "Received"
    ACKNOWLEDGED = "Acknowledged"
    UNDER_REVIEW = "Under Review"
    ASSIGNED = "Assigned"
    UNDER_PROCESS = "Under Process"
    INVESTIGATION = "Investigation"
    PENDING_INFORMATION = "Pending Information"
    TRANSFERRED = "Transferred"
    ESCALATED = "Escalated"
    DISPOSED = "Disposed"
    CLOSED = "Closed"
    REOPENED = "Reopened"


class ComplaintPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class SourceSystem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "source_systems"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    source_records = relationship("SourceRecord", back_populates="source_system")
    complaints = relationship("Complaint", back_populates="source_system")


class SourceRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "source_records"

    source_system_id = Column(UUID(as_uuid=True), ForeignKey("source_systems.id", ondelete="RESTRICT"), nullable=False, index=True)
    original_case_id = Column(String(150), nullable=False, index=True)
    payload_hash = Column(String(64), nullable=False, index=True)
    raw_payload = Column(JSONB, nullable=False)
    sync_timestamp = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    source_system = relationship("SourceSystem", back_populates="source_records")
    complaints = relationship("Complaint", back_populates="source_record")


class ComplaintCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "complaint_categories"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    severity_level = Column(String(20), default="Medium", nullable=False)
    default_sla_days = Column(Integer, default=30, nullable=False)

    # Relationships
    complaints = relationship("Complaint", back_populates="category")


class Complaint(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "complaints"

    complaint_number = Column(String(50), unique=True, nullable=False, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True)
    bureau_id = Column(UUID(as_uuid=True), ForeignKey("bureaus.id", ondelete="RESTRICT"), nullable=False, index=True)
    source_system_id = Column(UUID(as_uuid=True), ForeignKey("source_systems.id", ondelete="RESTRICT"), nullable=False, index=True)
    source_record_id = Column(UUID(as_uuid=True), ForeignKey("source_records.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("complaint_categories.id", ondelete="RESTRICT"), nullable=False, index=True)

    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    complainant_type = Column(String(50), default="Citizen", nullable=False)
    complainant_name = Column(String(150), nullable=True)
    complainant_email = Column(String(150), nullable=True)
    complainant_phone = Column(String(50), nullable=True)

    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.RECEIVED, nullable=False, index=True)
    priority = Column(Enum(ComplaintPriority), default=ComplaintPriority.MEDIUM, nullable=False, index=True)

    received_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    disposed_date = Column(DateTime(timezone=True), nullable=True)

    is_overlapping = Column(Boolean, default=False, nullable=False, index=True)
    vector_embedding = Column(JSONB, nullable=True)
    metadata_json = Column(JSONB, nullable=True)

    # Relationships
    institution = relationship("Institution", back_populates="complaints")
    bureau = relationship("Bureau", back_populates="complaints")
    source_system = relationship("SourceSystem", back_populates="complaints")
    source_record = relationship("SourceRecord", back_populates="complaints")
    category = relationship("ComplaintCategory", back_populates="complaints")
    cases = relationship("Case", back_populates="complaint")
    status_history = relationship("CaseStatusHistory", back_populates="complaint", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="complaint", cascade="all, delete-orphan")

