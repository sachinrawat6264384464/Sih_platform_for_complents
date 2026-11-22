from datetime import datetime, timedelta, timezone
import math
import secrets
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.case import Case, CaseAssignment, CaseStatusHistory
from app.models.complaint import Complaint, ComplaintCategory, ComplaintPriority, ComplaintStatus, SourceSystem
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, StatusTransitionRequest

# Valid 12-state workflow machine
VALID_TRANSITIONS: Dict[ComplaintStatus, List[ComplaintStatus]] = {
    ComplaintStatus.RECEIVED: [ComplaintStatus.ACKNOWLEDGED, ComplaintStatus.UNDER_REVIEW],
    ComplaintStatus.ACKNOWLEDGED: [ComplaintStatus.UNDER_REVIEW, ComplaintStatus.ASSIGNED],
    ComplaintStatus.UNDER_REVIEW: [ComplaintStatus.ASSIGNED, ComplaintStatus.UNDER_PROCESS, ComplaintStatus.TRANSFERRED],
    ComplaintStatus.ASSIGNED: [ComplaintStatus.UNDER_PROCESS, ComplaintStatus.INVESTIGATION, ComplaintStatus.TRANSFERRED],
    ComplaintStatus.UNDER_PROCESS: [ComplaintStatus.INVESTIGATION, ComplaintStatus.PENDING_INFORMATION, ComplaintStatus.TRANSFERRED, ComplaintStatus.ESCALATED, ComplaintStatus.DISPOSED],
    ComplaintStatus.INVESTIGATION: [ComplaintStatus.PENDING_INFORMATION, ComplaintStatus.ESCALATED, ComplaintStatus.DISPOSED],
    ComplaintStatus.PENDING_INFORMATION: [ComplaintStatus.UNDER_PROCESS, ComplaintStatus.INVESTIGATION, ComplaintStatus.CLOSED],
    ComplaintStatus.TRANSFERRED: [ComplaintStatus.ACKNOWLEDGED, ComplaintStatus.UNDER_REVIEW, ComplaintStatus.ASSIGNED],
    ComplaintStatus.ESCALATED: [ComplaintStatus.UNDER_PROCESS, ComplaintStatus.INVESTIGATION, ComplaintStatus.DISPOSED],
    ComplaintStatus.DISPOSED: [ComplaintStatus.CLOSED, ComplaintStatus.REOPENED],
    ComplaintStatus.CLOSED: [ComplaintStatus.REOPENED],
    ComplaintStatus.REOPENED: [ComplaintStatus.UNDER_REVIEW, ComplaintStatus.ASSIGNED, ComplaintStatus.INVESTIGATION],
}


def generate_complaint_number() -> str:
    year = datetime.now().year
    rand_seq = secrets.randbelow(900000) + 100000
    return f"AICTE-{year}-{rand_seq}"


def generate_case_number() -> str:
    year = datetime.now().year
    rand_seq = secrets.randbelow(900000) + 100000
    return f"CASE-{year}-{rand_seq}"


async def create_complaint(db: AsyncSession, data: ComplaintCreate, user_id: Optional[UUID] = None) -> Complaint:
    # Resolve source system if not provided
    source_sys_id = data.source_system_id
    if not source_sys_id:
        default_source = (await db.execute(select(SourceSystem).where(SourceSystem.code == "PGRC_PORTAL"))).scalar_one_or_none()
        if default_source:
            source_sys_id = default_source.id

    # Compute SLA due date from category default if not provided
    due_date = data.due_date
    if not due_date:
        cat = (await db.execute(select(ComplaintCategory).where(ComplaintCategory.id == data.category_id))).scalar_one_or_none()
        sla_days = cat.default_sla_days if cat else 30
        due_date = datetime.now(timezone.utc) + timedelta(days=sla_days)

    now = datetime.now(timezone.utc)
    complaint_no = generate_complaint_number()

    complaint = Complaint(
        complaint_number=complaint_no,
        institution_id=data.institution_id,
        bureau_id=data.bureau_id,
        source_system_id=source_sys_id,
        category_id=data.category_id,
        title=data.title,
        description=data.description,
        complainant_type=data.complainant_type,
        complainant_name=data.complainant_name,
        complainant_email=data.complainant_email,
        complainant_phone=data.complainant_phone,
        status=ComplaintStatus.RECEIVED,
        priority=data.priority,
        received_date=now,
        due_date=due_date,
        is_overlapping=False,
    )
    db.add(complaint)
    await db.flush()

    # Create associated Case record
    case_no = generate_case_number()
    case = Case(
        case_number=case_no,
        complaint_id=complaint.id,
        institution_id=complaint.institution_id,
        bureau_id=complaint.bureau_id,
        title=complaint.title,
        current_status="Received",
        sla_status="Within_SLA",
        expected_disposal_date=due_date,
    )
    db.add(case)
    await db.flush()

    # Record initial status in history
    status_history = CaseStatusHistory(
        case_id=case.id,
        complaint_id=complaint.id,
        previous_status=None,
        new_status=ComplaintStatus.RECEIVED.value,
        changed_by_id=user_id,
        remarks="Complaint received and registered in AICTE Nexus platform.",
        transition_reason="INITIAL_REGISTRATION",
    )
    db.add(status_history)

    await db.commit()
    await db.refresh(complaint)
    return complaint


async def get_complaint_by_id(db: AsyncSession, complaint_id: UUID) -> Optional[Complaint]:
    query = (
        select(Complaint)
        .options(
            selectinload(Complaint.institution),
            selectinload(Complaint.bureau),
            selectinload(Complaint.category),
            selectinload(Complaint.source_system),
            selectinload(Complaint.status_history),
            selectinload(Complaint.documents),
            selectinload(Complaint.cases),
        )
        .where(Complaint.id == complaint_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_complaints(
    db: AsyncSession,
    bureau_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
    status_filter: Optional[ComplaintStatus] = None,
    priority: Optional[ComplaintPriority] = None,
    is_overlapping: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> Dict[str, Any]:
    offset = (page - 1) * limit
    base_query = select(Complaint)

    conditions = []
    if bureau_id:
        conditions.append(Complaint.bureau_id == bureau_id)
    if institution_id:
        conditions.append(Complaint.institution_id == institution_id)
    if status_filter:
        conditions.append(Complaint.status == status_filter)
    if priority:
        conditions.append(Complaint.priority == priority)
    if is_overlapping is not None:
        conditions.append(Complaint.is_overlapping == is_overlapping)
    if search:
        search_filter = or_(
            Complaint.complaint_number.ilike(f"%{search}%"),
            Complaint.title.ilike(f"%{search}%"),
            Complaint.description.ilike(f"%{search}%"),
        )
        conditions.append(search_filter)

    if conditions:
        base_query = base_query.where(*conditions)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    items_query = (
        base_query.options(
            selectinload(Complaint.institution),
            selectinload(Complaint.bureau),
            selectinload(Complaint.category),
            selectinload(Complaint.source_system),
        )
        .order_by(Complaint.created_at.desc())
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


async def transition_complaint_status(
    db: AsyncSession,
    complaint_id: UUID,
    transition: StatusTransitionRequest,
    user_id: Optional[UUID] = None,
    is_superuser: bool = False,
) -> Complaint:
    complaint = await get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint record not found.")

    current = complaint.status
    target = transition.new_status

    if current == target:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Complaint is already in status '{target.value}'.",
        )

    # Validate state transition rules
    allowed = VALID_TRANSITIONS.get(current, [])
    if target not in allowed:
        allowed_names = [s.value for s in allowed]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current.value}' to '{target.value}'. Permitted transitions: {allowed_names}",
        )

    # Apply status change
    previous_val = complaint.status.value
    complaint.status = target

    if target == ComplaintStatus.DISPOSED:
        complaint.disposed_date = datetime.now(timezone.utc)

    # Synchronize linked case if exists
    linked_case = (await db.execute(select(Case).where(Case.complaint_id == complaint.id))).scalar_one_or_none()
    case_id = None
    if linked_case:
        linked_case.current_status = target.value
        case_id = linked_case.id

    # Append to chronological history
    history = CaseStatusHistory(
        case_id=case_id,
        complaint_id=complaint.id,
        previous_status=previous_val,
        new_status=target.value,
        changed_by_id=user_id,
        remarks=transition.remarks,
        transition_reason=transition.reason or "OFFICER_STATUS_UPDATE",
    )
    db.add(history)

    await db.commit()
    await db.refresh(complaint)
    return complaint


async def assign_complaint_officer(
    db: AsyncSession,
    complaint_id: UUID,
    officer_id: UUID,
    assigned_by_id: Optional[UUID] = None,
    role_description: str = "Lead Investigator",
) -> CaseAssignment:
    complaint = await get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found.")

    linked_case = (await db.execute(select(Case).where(Case.complaint_id == complaint.id))).scalar_one_or_none()
    if not linked_case:
        # Create case if missing
        linked_case = Case(
            case_number=generate_case_number(),
            complaint_id=complaint.id,
            institution_id=complaint.institution_id,
            bureau_id=complaint.bureau_id,
            title=complaint.title,
            current_status="Assigned",
        )
        db.add(linked_case)
        await db.flush()

    # Deactivate existing assignments
    existing_assignments = (await db.execute(
        select(CaseAssignment).where(CaseAssignment.case_id == linked_case.id, CaseAssignment.is_active == True)
    )).scalars().all()
    for ea in existing_assignments:
        ea.is_active = False
        ea.relieved_at = datetime.now(timezone.utc)

    # Create new assignment
    new_assignment = CaseAssignment(
        case_id=linked_case.id,
        officer_id=officer_id,
        assigned_by_id=assigned_by_id,
        role_description=role_description,
        is_active=True,
        assigned_at=datetime.now(timezone.utc),
    )
    db.add(new_assignment)

    # Progress status to ASSIGNED if currently RECEIVED or ACKNOWLEDGED
    if complaint.status in [ComplaintStatus.RECEIVED, ComplaintStatus.ACKNOWLEDGED, ComplaintStatus.UNDER_REVIEW]:
        complaint.status = ComplaintStatus.ASSIGNED
        linked_case.current_status = ComplaintStatus.ASSIGNED.value
        db.add(CaseStatusHistory(
            case_id=linked_case.id,
            complaint_id=complaint.id,
            previous_status="Under Review",
            new_status=ComplaintStatus.ASSIGNED.value,
            changed_by_id=assigned_by_id,
            remarks=f"Assigned to investigating officer.",
            transition_reason="OFFICER_ASSIGNMENT",
        ))

    await db.commit()
    await db.refresh(new_assignment)
    return new_assignment
