from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.auth import Role, RolePermission, User, UserBureauAssignment, UserRole
from app.schemas.auth import UserCreate, UserOut, UserUpdate
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/officers", tags=["Officers & Workforce"])


@router.get("", response_model=List[UserOut])
async def list_officers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.permissions).selectinload(RolePermission.permission),
            selectinload(User.bureau_assignments).selectinload(UserBureauAssignment.bureau),
            selectinload(User.bureau_assignments).selectinload(UserBureauAssignment.regional_office),
        )
        .order_by(User.full_name)
    )
    users = (await db.execute(query)).scalars().all()

    items = []
    for u in users:
        role_codes = [ur.role.code for ur in u.roles if ur.role]
        if u.is_superuser:
            role_codes.append("SUPER_ADMIN")

        perms = set()
        if u.is_superuser:
            perms.add("*")
        else:
            for ur in u.roles:
                if ur.role:
                    for rp in ur.role.permissions:
                        if rp.permission:
                            perms.add(rp.permission.code)

        bureau_list = []
        for ba in u.bureau_assignments:
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

        items.append(
            UserOut(
                id=u.id,
                username=u.username,
                email=u.email,
                full_name=u.full_name,
                phone=u.phone,
                designation=u.designation,
                is_active=u.is_active,
                is_superuser=u.is_superuser,
                last_login_at=u.last_login_at,
                roles=list(set(role_codes)),
                permissions=list(perms),
                bureau_assignments=bureau_list,
            )
        )
    return items


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_officer(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("USER_MANAGE")),
):
    existing = (await db.execute(select(User).where((User.username == data.username) | (User.email == data.email)))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered.")

    hashed_pw = get_password_hash(data.password)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_pw,
        full_name=data.full_name,
        phone=data.phone,
        designation=data.designation,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.flush()

    # Assign roles
    for r_code in data.role_codes:
        role = (await db.execute(select(Role).where(Role.code == r_code))).scalar_one_or_none()
        if role:
            db.add(UserRole(user_id=user.id, role_id=role.id))

    # Assign bureau / region
    if data.bureau_id or data.regional_office_id:
        db.add(UserBureauAssignment(
            user_id=user.id,
            bureau_id=data.bureau_id,
            regional_office_id=data.regional_office_id,
            is_primary=True,
            role_title=data.designation or "Case Officer"
        ))

    await record_audit_log(
        db,
        action="CREATE_OFFICER",
        entity_type="USER",
        entity_id=user.id,
        user_id=current_user.id,
        changes={"username": user.username, "roles": data.role_codes}
    )
    await db.commit()

    return await get_officer_out(db, user.id)


async def get_officer_out(db: AsyncSession, user_id: UUID) -> UserOut:
    query = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.permissions).selectinload(RolePermission.permission),
            selectinload(User.bureau_assignments).selectinload(UserBureauAssignment.bureau),
            selectinload(User.bureau_assignments).selectinload(UserBureauAssignment.regional_office),
        )
        .where(User.id == user_id)
    )
    u = (await db.execute(query)).scalar_one()
    role_codes = [ur.role.code for ur in u.roles if ur.role]
    perms = {rp.permission.code for ur in u.roles if ur.role for rp in ur.role.permissions if rp.permission}
    return UserOut(
        id=u.id,
        username=u.username,
        email=u.email,
        full_name=u.full_name,
        phone=u.phone,
        designation=u.designation,
        is_active=u.is_active,
        is_superuser=u.is_superuser,
        last_login_at=u.last_login_at,
        roles=role_codes,
        permissions=list(perms),
        bureau_assignments=[
            {
                "id": ba.id,
                "bureau_id": ba.bureau_id,
                "bureau_name": ba.bureau.name if ba.bureau else None,
                "bureau_code": ba.bureau.code if ba.bureau else None,
                "regional_office_id": ba.regional_office_id,
                "regional_office_name": ba.regional_office.name if ba.regional_office else None,
                "is_primary": ba.is_primary,
                "role_title": ba.role_title,
            }
            for ba in u.bureau_assignments
        ]
    )

