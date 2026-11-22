from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class AgentRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "agent_runs"

    agent_name = Column(String(100), nullable=False, index=True)
    workflow_id = Column(String(100), nullable=True, index=True)
    input_state = Column(JSONB, nullable=False)
    output_state = Column(JSONB, nullable=True)
    status = Column(String(50), default="RUNNING", nullable=False)  # RUNNING, COMPLETED, FAILED
    duration_ms = Column(Float, default=0.0, nullable=False)

    # Relationships
    steps = relationship("AgentStep", back_populates="run", cascade="all, delete-orphan")


class AgentStep(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "agent_steps"

    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    node_name = Column(String(100), nullable=False)
    state_snapshot = Column(JSONB, nullable=False)
    reasoning_trace = Column(Text, nullable=True)

    # Relationships
    run = relationship("AgentRun", back_populates="steps")


class RetrievalLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "retrieval_logs"

    query_text = Column(Text, nullable=False)
    bm25_matches_count = Column(Integer, default=0, nullable=False)
    vector_matches_count = Column(Integer, default=0, nullable=False)
    hybrid_results = Column(JSONB, nullable=True)
    latency_ms = Column(Float, default=0.0, nullable=False)


class ApprovalRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "approval_requests"

    request_type = Column(String(100), nullable=False, index=True)  # CONFIRM_OVERLAP, CASE_TRANSFER, ESCALATION, REGULATORY_ACTION
    reference_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    payload = Column(JSONB, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED
    reviewer_remarks = Column(Text, nullable=True)
