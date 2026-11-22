from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.auth import User
from app.schemas.case import (
    CaseActionCreate,
    CaseEscalationCreate,
    CaseListResponse,
    CaseOut,
    CaseTransferCreate,
    CaseTransferReview,
)
from app.services.audit_service import record_audit_log
from app.services.case_service import (
    add_case_action,
    get_case_by_id,
    initiate_case_transfer,
    list_cases,
    review_case_transfer,
)

router = APIRouter(prefix="/cases", tags=["Cases & Coordination"])


@router.get("", response_model=CaseListResponse)
async def get_cases(
    bureau_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    is_coordinated: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await list_cases(
        db,
        bureau_id=bureau_id,
        institution_id=institution_id,
        status_filter=status_filter,
        is_coordinated=is_coordinated,
        search=search,
        page=page,
        limit=limit,
    )
    return result


@router.get("/{case_id}", response_model=CaseOut)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = await get_case_by_id(db, case_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case record not found.")

    lead_officer = None
    for a in c.assignments:
        if a.is_active and a.officer:
            lead_officer = a.officer.full_name
            break

    return CaseOut(
        id=c.id,
        case_number=c.case_number,
        complaint_id=c.complaint_id,
        complaint_number=c.complaint.complaint_number if c.complaint else None,
        institution_id=c.institution_id,
        institution_name=c.institution.name if c.institution else None,
        aicte_permanent_id=c.institution.aicte_permanent_id if c.institution else None,
        bureau_id=c.bureau_id,
        bureau_name=c.bureau.name if c.bureau else None,
        lead_bureau_id=c.lead_bureau_id,
        lead_bureau_name=c.lead_bureau.name if c.lead_bureau else None,
        title=c.title,
        current_status=c.current_status,
        coordination_notes=c.coordination_notes,
        is_coordinated=c.is_coordinated,
        sla_status=c.sla_status,
        expected_disposal_date=c.expected_disposal_date,
        assigned_officer_name=lead_officer,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.post("/{case_id}/action", status_code=status.HTTP_201_CREATED)
async def create_action(
    case_id: UUID,
    action_data: CaseActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("CASE_COORDINATE")),
):
    action = await add_case_action(db, case_id, action_data, user_id=current_user.id)
    await record_audit_log(
        db,
        action="ADD_ACTION",
        entity_type="CASE",
        entity_id=case_id,
        user_id=current_user.id,
        changes={"type": action_data.action_type, "title": action_data.action_title}
    )
    await db.commit()
    return {"message": "Case action logged successfully.", "action_id": action.id}


@router.post("/{case_id}/transfer", status_code=status.HTTP_201_CREATED)
async def request_transfer(
    case_id: UUID,
    transfer_data: CaseTransferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("CASE_TRANSFER")),
):
    transfer = await initiate_case_transfer(db, case_id, transfer_data, user_id=current_user.id)
    await record_audit_log(
        db,
        action="INITIATE_TRANSFER",
        entity_type="CASE",
        entity_id=case_id,
        user_id=current_user.id,
        changes={"target_bureau_id": str(transfer_data.target_bureau_id), "reason": transfer_data.reason}
    )
    await db.commit()
    return {"message": "Transfer proposal initiated successfully.", "transfer_id": transfer.id}


@router.post("/transfer/{transfer_id}/review")
async def review_transfer(
    transfer_id: UUID,
    review: CaseTransferReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("CASE_TRANSFER")),
):
    transfer = await review_case_transfer(db, transfer_id, review, reviewer_id=current_user.id)
    await record_audit_log(
        db,
        action="REVIEW_TRANSFER",
        entity_type="CASE_TRANSFER",
        entity_id=transfer_id,
        user_id=current_user.id,
        changes={"approved": review.approved, "remarks": review.decision_remarks}
    )
    await db.commit()
    return {"message": f"Transfer {'approved' if review.approved else 'rejected'} successfully."}

