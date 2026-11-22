from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.case import Case, CaseAction, CaseAssignment, CaseEscalation, CaseRelationship, CaseTransfer
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.case import CaseActionCreate, CaseEscalationCreate, CaseTransferCreate, CaseTransferReview


async def list_cases(
    db: AsyncSession,
    bureau_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    is_coordinated: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    offset = (page - 1) * limit
    base_query = select(Case)

    conditions = []
    if bureau_id:
        conditions.append(or_(Case.bureau_id == bureau_id, Case.lead_bureau_id == bureau_id))
    if institution_id:
        conditions.append(Case.institution_id == institution_id)
    if status_filter:
        conditions.append(Case.current_status == status_filter)
    if is_coordinated is not None:
        conditions.append(Case.is_coordinated == is_coordinated)
    if search:
        conditions.append(or_(
            Case.case_number.ilike(f"%{search}%"),
            Case.title.ilike(f"%{search}%"),
        ))

    if conditions:
        base_query = base_query.where(*conditions)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    items_query = (
        base_query.options(
            selectinload(Case.institution),
            selectinload(Case.bureau),
            selectinload(Case.lead_bureau),
            selectinload(Case.complaint),
            selectinload(Case.assignments).selectinload(CaseAssignment.officer),
        )
        .order_by(Case.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    cases = (await db.execute(items_query)).scalars().all()

    items = []
    for c in cases:
        lead_officer = None
        for a in c.assignments:
            if a.is_active and a.officer:
                lead_officer = a.officer.full_name
                break

        items.append({
            "id": c.id,
            "case_number": c.case_number,
            "complaint_id": c.complaint_id,
            "complaint_number": c.complaint.complaint_number if c.complaint else None,
            "institution_id": c.institution_id,
            "institution_name": c.institution.name if c.institution else None,
            "aicte_permanent_id": c.institution.aicte_permanent_id if c.institution else None,
            "bureau_id": c.bureau_id,
            "bureau_name": c.bureau.name if c.bureau else None,
            "lead_bureau_id": c.lead_bureau_id,
            "lead_bureau_name": c.lead_bureau.name if c.lead_bureau else None,
            "title": c.title,
            "current_status": c.current_status,
            "coordination_notes": c.coordination_notes,
            "is_coordinated": c.is_coordinated,
            "sla_status": c.sla_status,
            "expected_disposal_date": c.expected_disposal_date,
            "assigned_officer_name": lead_officer,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        })

    pages = math.ceil(total / limit) if limit > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


async def get_case_by_id(db: AsyncSession, case_id: UUID) -> Optional[Case]:
    query = (
        select(Case)
        .options(
            selectinload(Case.institution),
            selectinload(Case.bureau),
            selectinload(Case.lead_bureau),
            selectinload(Case.complaint),
            selectinload(Case.assignments).selectinload(CaseAssignment.officer),
            selectinload(Case.actions),
            selectinload(Case.transfers),
            selectinload(Case.escalations),
        )
        .where(Case.id == case_id)
    )
    return (await db.execute(query)).scalar_one_or_none()


async def add_case_action(
    db: AsyncSession,
    case_id: UUID,
    action_data: CaseActionCreate,
    user_id: Optional[UUID] = None
) -> CaseAction:
    c = await get_case_by_id(db, case_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case record not found.")

    action = CaseAction(
        case_id=case_id,
        action_type=action_data.action_type,
        action_title=action_data.action_title,
        action_details=action_data.action_details,
        performed_by_id=user_id,
        action_date=action_data.action_date or datetime.now(timezone.utc),
    )
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action


async def initiate_case_transfer(
    db: AsyncSession,
    case_id: UUID,
    transfer_data: CaseTransferCreate,
    user_id: Optional[UUID] = None
) -> CaseTransfer:
    c = await get_case_by_id(db, case_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case record not found.")

    transfer = CaseTransfer(
        case_id=case_id,
        source_bureau_id=c.bureau_id,
        target_bureau_id=transfer_data.target_bureau_id,
        initiated_by_id=user_id,
        reason=transfer_data.reason,
        transfer_status="Pending",
    )
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    return transfer


async def review_case_transfer(
    db: AsyncSession,
    transfer_id: UUID,
    review: CaseTransferReview,
    reviewer_id: Optional[UUID] = None
) -> CaseTransfer:
    transfer = (await db.execute(select(CaseTransfer).where(CaseTransfer.id == transfer_id))).scalar_one_or_none()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer request not found.")

    transfer.transfer_status = "Approved" if review.approved else "Rejected"
    transfer.decision_remarks = review.decision_remarks
    transfer.reviewed_by_id = reviewer_id

    if review.approved:
        case_rec = await get_case_by_id(db, transfer.case_id)
        if case_rec:
            case_rec.bureau_id = transfer.target_bureau_id
            case_rec.current_status = "Transferred"
            if case_rec.complaint:
                case_rec.complaint.bureau_id = transfer.target_bureau_id
                case_rec.complaint.status = ComplaintStatus.TRANSFERRED

    await db.commit()
    await db.refresh(transfer)
    return transfer

