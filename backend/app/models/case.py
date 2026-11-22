from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Case(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cases"

    case_number = Column(String(50), unique=True, nullable=False, index=True)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True)
    bureau_id = Column(UUID(as_uuid=True), ForeignKey("bureaus.id", ondelete="RESTRICT"), nullable=False, index=True)
    lead_bureau_id = Column(UUID(as_uuid=True), ForeignKey("bureaus.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String(300), nullable=False)
    current_status = Column(String(50), default="Under Review", nullable=False, index=True)
    coordination_notes = Column(Text, nullable=True)
    is_coordinated = Column(Boolean, default=False, nullable=False, index=True)
    sla_status = Column(String(50), default="Within_SLA", nullable=False, index=True)
    expected_disposal_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    complaint = relationship("Complaint", back_populates="cases")
    institution = relationship("Institution", back_populates="cases")
    bureau = relationship("Bureau", foreign_keys=[bureau_id], back_populates="cases")
    lead_bureau = relationship("Bureau", foreign_keys=[lead_bureau_id])
    assignments = relationship("CaseAssignment", back_populates="case", cascade="all, delete-orphan")
    actions = relationship("CaseAction", back_populates="case", cascade="all, delete-orphan")
    transfers = relationship("CaseTransfer", back_populates="case", cascade="all, delete-orphan")
    escalations = relationship("CaseEscalation", back_populates="case", cascade="all, delete-orphan")


class CaseAssignment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "case_assignments"

    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    role_description = Column(String(100), default="Lead Investigator", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    assigned_at = Column(DateTime(timezone=True), nullable=False)
    relieved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    case = relationship("Case", back_populates="assignments")
    officer = relationship("User", foreign_keys=[officer_id], back_populates="assigned_cases")


class CaseStatusHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "case_status_history"

    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=False)
    transition_reason = Column(String(200), nullable=True)

    # Relationships
    complaint = relationship("Complaint", back_populates="status_history")


class CaseAction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "case_actions"

    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # Inspection, Show Cause Notice, Hearing, Penalty, Coordination Note
    action_title = Column(String(200), nullable=False)
    action_details = Column(Text, nullable=False)
    performed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_date = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    case = relationship("Case", back_populates="actions")


class CaseTransfer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "case_transfers"

    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    source_bureau_id = Column(UUID(as_uuid=True), ForeignKey("bureaus.id", ondelete="RESTRICT"), nullable=False)
    target_bureau_id = Column(UUID(as_uuid=True), ForeignKey("bureaus.id", ondelete="RESTRICT"), nullable=False)
    initiated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason = Column(Text, nullable=False)
    transfer_status = Column(String(50), default="Pending", nullable=False)  # Pending, Approved, Rejected
    decision_remarks = Column(Text, nullable=True)

    # Relationships
    case = relationship("Case", back_populates="transfers")


class CaseEscalation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "case_escalations"

    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    escalation_level = Column(Integer, default=1, nullable=False)
    reason = Column(Text, nullable=False)
    escalated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    escalated_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="Open", nullable=False)

    # Relationships
    case = relationship("Case", back_populates="escalations")


class CaseRelationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "case_relationships"

    source_case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    target_case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)  # Linked, Duplicate, Coordinated, Cross_Bureau
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

