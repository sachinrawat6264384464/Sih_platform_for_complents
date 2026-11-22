from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.auth import User
from app.models.bureau import Bureau, RegionalOffice
from app.models.complaint import Complaint
from app.schemas.bureau import (
    BureauCreate,
    BureauOut,
    BureauUpdate,
    RegionalOfficeCreate,
    RegionalOfficeOut,
    RegionalOfficeUpdate,
)

router = APIRouter(prefix="/bureaus", tags=["Bureaus & Regions"])


@router.get("", response_model=List[BureauOut])
async def get_bureaus(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    bureaus = (await db.execute(select(Bureau).order_by(Bureau.name))).scalars().all()
    results = []
    for b in bureaus:
        count = (await db.execute(select(func.count(Complaint.id)).where(Complaint.bureau_id == b.id))).scalar_one()
        results.append(BureauOut(
            id=b.id,
            code=b.code,
            name=b.name,
            description=b.description,
            is_active=b.is_active,
            contact_email=b.contact_email,
            contact_phone=b.contact_phone,
            escalation_level=b.escalation_level,
            active_cases_count=count,
            created_at=b.created_at,
            updated_at=b.updated_at,
        ))
    return results


@router.post("", response_model=BureauOut, status_code=status.HTTP_201_CREATED)
async def create_bureau(
    data: BureauCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("BUREAU_MANAGE")),
):
    existing = (await db.execute(select(Bureau).where(Bureau.code == data.code))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bureau code '{data.code}' already exists.")

    bureau = Bureau(**data.model_dump())
    db.add(bureau)
    await db.commit()
    await db.refresh(bureau)
    return BureauOut(
        id=bureau.id,
        code=bureau.code,
        name=bureau.name,
        description=bureau.description,
        is_active=bureau.is_active,
        contact_email=bureau.contact_email,
        contact_phone=bureau.contact_phone,
        escalation_level=bureau.escalation_level,
        active_cases_count=0,
        created_at=bureau.created_at,
        updated_at=bureau.updated_at,
    )


@router.get("/regions", response_model=List[RegionalOfficeOut])
async def get_regions(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    regions = (await db.execute(select(RegionalOffice).order_by(RegionalOffice.name))).scalars().all()
    return regions


@router.post("/regions", response_model=RegionalOfficeOut, status_code=status.HTTP_201_CREATED)
async def create_region(
    data: RegionalOfficeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("BUREAU_MANAGE")),
):
    reg = RegionalOffice(**data.model_dump())
    db.add(reg)
    await db.commit()
    await db.refresh(reg)
    return reg

