from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class OverlapCandidate(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "overlap_candidates"

    complaint_a_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    complaint_b_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True)

    stage1_exact_id_score = Column(Float, default=0.0, nullable=False)
    stage2_name_fuzzy_score = Column(Float, default=0.0, nullable=False)
    stage3_geo_score = Column(Float, default=0.0, nullable=False)
    stage4_category_score = Column(Float, default=0.0, nullable=False)
    stage5_bm25_score = Column(Float, default=0.0, nullable=False)
    stage6_vector_score = Column(Float, default=0.0, nullable=False)
    stage7_bureau_score = Column(Float, default=0.0, nullable=False)
    total_confidence_score = Column(Float, default=0.0, nullable=False, index=True)

    match_reasons = Column(JSONB, nullable=False)  # List of textual explanations
    status = Column(String(50), default="Pending", nullable=False, index=True)  # Pending, Confirmed, False_Positive, Linked

    # Relationships
    complaint_a = relationship("Complaint", foreign_keys=[complaint_a_id])
    complaint_b = relationship("Complaint", foreign_keys=[complaint_b_id])
    institution = relationship("Institution")
    reviews = relationship("OverlapReview", back_populates="candidate", cascade="all, delete-orphan")


class OverlapReview(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "overlap_reviews"

    overlap_candidate_id = Column(UUID(as_uuid=True), ForeignKey("overlap_candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    verdict = Column(String(50), nullable=False)  # Confirmed, False_Positive, Linked
    remarks = Column(Text, nullable=False)

    # Relationships
    candidate = relationship("OverlapCandidate", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")

