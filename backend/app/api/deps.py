from typing import AsyncGenerator, Callable, List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import decode_token
from app.models.auth import Role, RolePermission, User, UserBureauAssignment, UserRole

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not auth_header or not auth_header.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired or malformed access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject identifier missing",
        )

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
        )

    # Fetch user with roles, permissions, bureau assignments
    query = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.permissions).selectinload(RolePermission.permission),
            selectinload(User.bureau_assignments).selectinload(UserBureauAssignment.bureau),
            selectinload(User.bureau_assignments).selectinload(UserBureauAssignment.regional_office),
        )
        .where(User.id == user_uuid)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account associated with token not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact AICTE administrator.",
        )

    return user


async def get_optional_current_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not auth_header or not auth_header.credentials:
        return None
    try:
        token = auth_header.credentials
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user_uuid = UUID(user_id_str)
        query = select(User).where(User.id == user_uuid)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except Exception:
        return None


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Administrator clearance required for this operation",
        )
    return current_user


def get_user_permissions(user: User) -> set[str]:
    perms = set()
    if user.is_superuser:
        return {"*"}  # Wildcard superuser
    for ur in user.roles:
        if ur.role:
            for rp in ur.role.permissions:
                if rp.permission:
                    perms.add(rp.permission.code)
    return perms


def get_user_roles(user: User) -> set[str]:
    roles = set()
    if user.is_superuser:
        roles.add("SUPER_ADMIN")
    for ur in user.roles:
        if ur.role:
            roles.add(ur.role.code)
    return roles


def require_permission(permission_code: str) -> Callable:
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user
        perms = get_user_permissions(current_user)
        if "*" in perms or permission_code in perms:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Missing required permission '{permission_code}'",
        )
    return permission_checker


def require_role(role_codes: List[str]) -> Callable:
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user
        roles = get_user_roles(current_user)
        if any(r in roles for r in role_codes):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Requires one of roles {role_codes}",
        )
    return role_checker

