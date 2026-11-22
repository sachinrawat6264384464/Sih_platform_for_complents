from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Bureau(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bureaus"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    contact_email = Column(String(100), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    escalation_level = Column(Integer, default=1, nullable=False)

    # Relationships
    user_assignments = relationship("UserBureauAssignment", back_populates="bureau", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="bureau")
    cases = relationship("Case", foreign_keys="Case.bureau_id", back_populates="bureau")


class RegionalOffice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "regional_offices"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    jurisdiction_states = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    institutions = relationship("Institution", back_populates="regional_office")
    user_assignments = relationship("UserBureauAssignment", back_populates="regional_office")
