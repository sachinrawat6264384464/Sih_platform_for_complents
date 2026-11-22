from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.models.auth import Role, RolePermission, User, UserBureauAssignment, UserRole
from app.schemas.auth import LoginRequest, Token, UserOut
from app.services.audit_service import record_audit_log, record_security_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.permissions).selectinload(RolePermission.permission),
            selectinload(User.bureau_assignments).selectinload(UserBureauAssignment.bureau),
        )
        .where(
            or_(
                User.username == login_data.username_or_email,
                User.email == login_data.username_or_email
            )
        )
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        await record_security_event(
            db,
            event_type="FAILED_LOGIN",
            details={"username_or_email": login_data.username_or_email},
            request=request
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact AICTE administrator.",
        )

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)

    # Build token claims
    role_codes = [ur.role.code for ur in user.roles if ur.role]
    if user.is_superuser:
        role_codes.append("SUPER_ADMIN")

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"username": user.username, "roles": role_codes}
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    await record_audit_log(
        db,
        action="LOGIN",
        entity_type="USER",
        entity_id=user.id,
        user_id=user.id,
        changes={"roles": role_codes},
        request=request
    )
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    role_codes = [ur.role.code for ur in current_user.roles if ur.role]
    if current_user.is_superuser:
        role_codes.append("SUPER_ADMIN")

    perms = set()
    if current_user.is_superuser:
        perms.add("*")
    else:
        for ur in current_user.roles:
            if ur.role:
                for rp in ur.role.permissions:
                    if rp.permission:
                        perms.add(rp.permission.code)

    bureau_list = []
    for ba in current_user.bureau_assignments:
        bureau_list.append({
            "id": ba.id,
            "bureau_id": ba.bureau_id,
            "bureau_name": ba.bureau.name if ba.bureau else None,
            "bureau_code": ba.bureau.code if ba.bureau else None,
            "regional_office_id": ba.regional_office_id,
            "regional_office_name": ba.regional_office.name if ba.regional_office else None,
            "is_primary": ba.is_primary,
            "role_title": ba.role_title,
        })

    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        designation=current_user.designation,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        last_login_at=current_user.last_login_at,
        roles=list(set(role_codes)),
        permissions=list(perms),
        bureau_assignments=bureau_list,
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")

    new_access = create_access_token(subject=str(user.id))
    new_refresh = create_refresh_token(subject=str(user.id))

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=3600
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await record_audit_log(
        db,
        action="LOGOUT",
        entity_type="USER",
        entity_id=current_user.id,
        user_id=current_user.id
    )
    await db.commit()
    return {"message": "Logged out successfully."}

