from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class IntegrationConfig(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integration_configs"

    name = Column(String(150), nullable=False)
    connector_type = Column(String(50), nullable=False, index=True)  # PGRC, RB, REGIONAL, EMAIL, CSV_SFTP
    base_url = Column(String(300), nullable=True)
    auth_type = Column(String(50), default="API_KEY", nullable=False)  # OAUTH2, API_KEY, BASIC, SFTP_KEY
    encrypted_credentials = Column(JSONB, nullable=True)
    sync_frequency_minutes = Column(Integer, default=60, nullable=False)
    webhook_secret = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_paused = Column(Boolean, default=False, nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_sync_status = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    field_mappings = relationship("IntegrationFieldMapping", back_populates="config", cascade="all, delete-orphan")
    sync_runs = relationship("IntegrationSyncRun", back_populates="config", cascade="all, delete-orphan")
    failures = relationship("IntegrationFailure", back_populates="config", cascade="all, delete-orphan")


class IntegrationFieldMapping(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integration_field_mappings"

    integration_config_id = Column(UUID(as_uuid=True), ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    source_field = Column(String(100), nullable=False)
    canonical_field = Column(String(100), nullable=False)
    transformation_rule = Column(String(100), nullable=True)  # uppercase, trim, date_iso, regex

    # Relationships
    config = relationship("IntegrationConfig", back_populates="field_mappings")


class IntegrationSyncRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integration_sync_runs"

    integration_config_id = Column(UUID(as_uuid=True), ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="Running", nullable=False)  # Running, Success, Partial, Failed
    records_fetched = Column(Integer, default=0, nullable=False)
    records_imported = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    details = Column(JSONB, nullable=True)

    # Relationships
    config = relationship("IntegrationConfig", back_populates="sync_runs")


class IntegrationFailure(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integration_failures"

    integration_config_id = Column(UUID(as_uuid=True), ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    sync_run_id = Column(UUID(as_uuid=True), ForeignKey("integration_sync_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    original_identifier = Column(String(150), nullable=True, index=True)
    raw_record = Column(JSONB, nullable=False)
    error_reason = Column(Text, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    config = relationship("IntegrationConfig", back_populates="failures")
