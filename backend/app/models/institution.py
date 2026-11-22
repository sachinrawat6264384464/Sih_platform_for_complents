from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Institution(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "institutions"

    aicte_permanent_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False, index=True)
    alternate_names = Column(ARRAY(String), nullable=True)
    institution_type = Column(String(100), nullable=False, default="Private")
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    pincode = Column(String(20), nullable=True)
    contact_email = Column(String(150), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    regional_office_id = Column(UUID(as_uuid=True), ForeignKey("regional_offices.id", ondelete="SET NULL"), nullable=True, index=True)
    approval_status = Column(String(50), default="Approved", nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata_json = Column(JSONB, nullable=True)

    # Relationships
    regional_office = relationship("RegionalOffice", back_populates="institutions")
    aliases = relationship("InstitutionAlias", back_populates="institution", cascade="all, delete-orphan")
    identifiers = relationship("InstitutionIdentifier", back_populates="institution", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="institution")
    cases = relationship("Case", back_populates="institution")


class InstitutionAlias(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "institution_aliases"

    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    alias_name = Column(String(300), nullable=False, index=True)
    alias_type = Column(String(50), default="Acronym", nullable=False)  # Acronym, Historical, Alternate

    # Relationships
    institution = relationship("Institution", back_populates="aliases")


class InstitutionIdentifier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "institution_identifiers"

    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    identifier_type = Column(String(50), nullable=False)  # AISHE, UGC, Affiliated_University
    identifier_value = Column(String(100), nullable=False, index=True)

    # Relationships
    institution = relationship("Institution", back_populates="identifiers")

