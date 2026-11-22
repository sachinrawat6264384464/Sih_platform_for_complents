from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.auth import User
from app.schemas.institution import InstitutionCreate, InstitutionListResponse, InstitutionOut, InstitutionUpdate
from app.services.audit_service import record_audit_log
from app.services.institution_service import (
    archive_institution,
    create_institution,
    get_institution_by_id,
    get_institution_by_permanent_id,
    list_institutions,
    update_institution,
)

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get("", response_model=InstitutionListResponse)
async def get_institutions(
    search: Optional[str] = Query(None, description="Search by name, permanent ID, or city"),
    state: Optional[str] = None,
    district: Optional[str] = None,
    institution_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    is_active: Optional[bool] = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await list_institutions(
        db,
        search=search,
        state=state,
        district=district,
        institution_type=institution_type,
        approval_status=approval_status,
        is_active=is_active,
        page=page,
        limit=limit,
    )
    return result


@router.post("", response_model=InstitutionOut, status_code=status.HTTP_201_CREATED)
async def add_institution(
    data: InstitutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("INSTITUTION_CREATE")),
):
    institution = await create_institution(db, data)
    await record_audit_log(
        db,
        action="CREATE",
        entity_type="INSTITUTION",
        entity_id=institution.id,
        user_id=current_user.id,
        changes={"aicte_permanent_id": institution.aicte_permanent_id, "name": institution.name}
    )
    await db.commit()
    return institution


@router.get("/{inst_id}", response_model=InstitutionOut)
async def get_institution_detail(
    inst_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inst = await get_institution_by_id(db, inst_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return inst


@router.get("/permanent-id/{permanent_id}", response_model=InstitutionOut)
async def get_institution_by_pid(
    permanent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inst = await get_institution_by_permanent_id(db, permanent_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Institution with Permanent ID '{permanent_id}' not found")
    return inst


@router.put("/{inst_id}", response_model=InstitutionOut)
async def edit_institution(
    inst_id: UUID,
    data: InstitutionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("INSTITUTION_UPDATE")),
):
    updated = await update_institution(db, inst_id, data)
    await record_audit_log(
        db,
        action="UPDATE",
        entity_type="INSTITUTION",
        entity_id=inst_id,
        user_id=current_user.id,
        changes=data.model_dump(exclude_unset=True)
    )
    await db.commit()
    return updated


@router.delete("/{inst_id}", response_model=InstitutionOut)
async def delete_institution(
    inst_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("INSTITUTION_ARCHIVE")),
):
    archived = await archive_institution(db, inst_id)
    await record_audit_log(
        db,
        action="ARCHIVE",
        entity_type="INSTITUTION",
        entity_id=inst_id,
        user_id=current_user.id
    )
    await db.commit()
    return archived

