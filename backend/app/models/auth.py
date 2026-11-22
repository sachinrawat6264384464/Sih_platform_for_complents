from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    designation = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    bureau_assignments = relationship("UserBureauAssignment", back_populates="user", cascade="all, delete-orphan")
    assigned_cases = relationship("CaseAssignment", foreign_keys="CaseAssignment.officer_id", back_populates="officer")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    reviews = relationship("OverlapReview", back_populates="reviewer")


class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)

    # Relationships
    users = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


class Permission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "permissions"

    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    module = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class UserRole(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


class RolePermission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


class UserBureauAssignment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_bureau_assignments"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bureau_id = Column(UUID(as_uuid=True), ForeignKey("bureaus.id", ondelete="SET NULL"), nullable=True, index=True)
    regional_office_id = Column(UUID(as_uuid=True), ForeignKey("regional_offices.id", ondelete="SET NULL"), nullable=True, index=True)
    is_primary = Column(Boolean, default=True, nullable=False)
    role_title = Column(String(150), nullable=True)

    # Relationships
    user = relationship("User", back_populates="bureau_assignments")
    bureau = relationship("Bureau", back_populates="user_assignments")
    regional_office = relationship("RegionalOffice", back_populates="user_assignments")
