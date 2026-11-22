import math
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.institution import Institution, InstitutionAlias, InstitutionIdentifier
from app.schemas.institution import InstitutionCreate, InstitutionUpdate


async def create_institution(db: AsyncSession, data: InstitutionCreate) -> Institution:
    # Check uniqueness of aicte_permanent_id
    existing = await db.execute(select(Institution).where(Institution.aicte_permanent_id == data.aicte_permanent_id))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Institution with AICTE Permanent ID '{data.aicte_permanent_id}' already exists.",
        )

    inst_data = data.model_dump(exclude={"alternate_names"})
    institution = Institution(**inst_data, alternate_names=data.alternate_names or [])
    db.add(institution)
    await db.flush()

    # Add alternate names as aliases
    if data.alternate_names:
        for alt in data.alternate_names:
            alias = InstitutionAlias(institution_id=institution.id, alias_name=alt, alias_type="Alternate")
            db.add(alias)

    await db.commit()
    return await get_institution_by_id(db, institution.id)


async def get_institution_by_id(db: AsyncSession, inst_id: UUID) -> Optional[Institution]:
    query = (
        select(Institution)
        .options(
            selectinload(Institution.regional_office),
            selectinload(Institution.aliases),
            selectinload(Institution.identifiers),
        )
        .where(Institution.id == inst_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_institution_by_permanent_id(db: AsyncSession, permanent_id: str) -> Optional[Institution]:
    query = (
        select(Institution)
        .options(
            selectinload(Institution.regional_office),
            selectinload(Institution.aliases),
            selectinload(Institution.identifiers),
        )
        .where(Institution.aicte_permanent_id == permanent_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_institutions(
    db: AsyncSession,
    search: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    institution_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    is_active: Optional[bool] = True,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    offset = (page - 1) * limit
    base_query = select(Institution)

    conditions = []
    if is_active is not None:
        conditions.append(Institution.is_active == is_active)
    if state:
        conditions.append(Institution.state.ilike(f"%{state}%"))
    if district:
        conditions.append(Institution.district.ilike(f"%{district}%"))
    if institution_type:
        conditions.append(Institution.institution_type == institution_type)
    if approval_status:
        conditions.append(Institution.approval_status == approval_status)
    if search:
        search_filter = or_(
            Institution.name.ilike(f"%{search}%"),
            Institution.aicte_permanent_id.ilike(f"%{search}%"),
            Institution.city.ilike(f"%{search}%"),
            Institution.district.ilike(f"%{search}%"),
        )
        conditions.append(search_filter)

    if conditions:
        base_query = base_query.where(*conditions)

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Fetch paginated items
    items_query = (
        base_query.options(
            selectinload(Institution.regional_office),
            selectinload(Institution.aliases),
            selectinload(Institution.identifiers),
        )
        .order_by(Institution.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(items_query)
    items = result.scalars().all()

    pages = math.ceil(total / limit) if limit > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


async def update_institution(db: AsyncSession, inst_id: UUID, data: InstitutionUpdate) -> Institution:
    inst = await get_institution_by_id(db, inst_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(inst, field, val)

    await db.commit()
    await db.refresh(inst)
    return inst


async def archive_institution(db: AsyncSession, inst_id: UUID) -> Institution:
    inst = await get_institution_by_id(db, inst_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    inst.is_active = False
    await db.commit()
    await db.refresh(inst)
    return inst
