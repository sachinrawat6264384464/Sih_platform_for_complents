from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.graph import orchestrator
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.auth import User
from app.models.complaint import ComplaintCategory, ComplaintPriority, ComplaintStatus, SourceSystem
from app.schemas.complaint import (
    CategoryOut,
    ComplaintCreate,
    ComplaintListResponse,
    ComplaintOut,
    SourceSystemOut,
    StatusTransitionRequest,
)
from app.services.audit_service import record_audit_log
from app.services.complaint_service import (
    assign_complaint_officer,
    create_complaint,
    get_complaint_by_id,
    list_complaints,
    transition_complaint_status,
)
from app.services.overlap_engine import scan_complaint_for_overlaps

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.get("/categories", response_model=List[CategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    cats = (await db.execute(select(ComplaintCategory).order_by(ComplaintCategory.name))).scalars().all()
    return cats


@router.get("/source-systems", response_model=List[SourceSystemOut])
async def get_source_systems(db: AsyncSession = Depends(get_db)):
    sources = (await db.execute(select(SourceSystem).order_by(SourceSystem.name))).scalars().all()
    return sources


@router.get("", response_model=ComplaintListResponse)
async def get_complaints(
    bureau_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
    status_filter: Optional[ComplaintStatus] = Query(None, alias="status"),
    priority: Optional[ComplaintPriority] = None,
    is_overlapping: Optional[bool] = None,
    search: Optional[str] = Query(None, description="Search complaint number, title or description"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await list_complaints(
        db,
        bureau_id=bureau_id,
        institution_id=institution_id,
        status_filter=status_filter,
        priority=priority,
        is_overlapping=is_overlapping,
        search=search,
        page=page,
        limit=limit,
    )

    items_out = []
    for c in result["items"]:
        items_out.append(
            ComplaintOut(
                id=c.id,
                complaint_number=c.complaint_number,
                institution_id=c.institution_id,
                institution_name=c.institution.name if c.institution else None,
                aicte_permanent_id=c.institution.aicte_permanent_id if c.institution else None,
                bureau_id=c.bureau_id,
                bureau_name=c.bureau.name if c.bureau else None,
                bureau_code=c.bureau.code if c.bureau else None,
                source_system_id=c.source_system_id,
                source_system_name=c.source_system.name if c.source_system else None,
                category_id=c.category_id,
                category_name=c.category.name if c.category else None,
                title=c.title,
                description=c.description,
                complainant_type=c.complainant_type,
                complainant_name=c.complainant_name,
                status=c.status,
                priority=c.priority,
                received_date=c.received_date,
                due_date=c.due_date,
                disposed_date=c.disposed_date,
                is_overlapping=c.is_overlapping,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return {
        "items": items_out,
        "total": result["total"],
        "page": result["page"],
        "limit": result["limit"],
        "pages": result["pages"],
    }


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def register_complaint(
    data: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("COMPLAINT_CREATE")),
):
    complaint = await create_complaint(db, data, user_id=current_user.id)
    
    # Run automatic overlap scan
    await scan_complaint_for_overlaps(db, complaint.id)

    await record_audit_log(
        db,
        action="CREATE",
        entity_type="COMPLAINT",
        entity_id=complaint.id,
        user_id=current_user.id,
        changes={"complaint_number": complaint.complaint_number, "title": complaint.title}
    )
    await db.commit()

    # Re-fetch with relationships
    c = await get_complaint_by_id(db, complaint.id)
    return ComplaintOut(
        id=c.id,
        complaint_number=c.complaint_number,
        institution_id=c.institution_id,
        institution_name=c.institution.name if c.institution else None,
        aicte_permanent_id=c.institution.aicte_permanent_id if c.institution else None,
        bureau_id=c.bureau_id,
        bureau_name=c.bureau.name if c.bureau else None,
        bureau_code=c.bureau.code if c.bureau else None,
        source_system_id=c.source_system_id,
        source_system_name=c.source_system.name if c.source_system else None,
        category_id=c.category_id,
        category_name=c.category.name if c.category else None,
        title=c.title,
        description=c.description,
        complainant_type=c.complainant_type,
        complainant_name=c.complainant_name,
        status=c.status,
        priority=c.priority,
        received_date=c.received_date,
        due_date=c.due_date,
        disposed_date=c.disposed_date,
        is_overlapping=c.is_overlapping,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.get("/{complaint_id}", response_model=ComplaintOut)
async def get_complaint(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = await get_complaint_by_id(db, complaint_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    return ComplaintOut(
        id=c.id,
        complaint_number=c.complaint_number,
        institution_id=c.institution_id,
        institution_name=c.institution.name if c.institution else None,
        aicte_permanent_id=c.institution.aicte_permanent_id if c.institution else None,
        bureau_id=c.bureau_id,
        bureau_name=c.bureau.name if c.bureau else None,
        bureau_code=c.bureau.code if c.bureau else None,
        source_system_id=c.source_system_id,
        source_system_name=c.source_system.name if c.source_system else None,
        category_id=c.category_id,
        category_name=c.category.name if c.category else None,
        title=c.title,
        description=c.description,
        complainant_type=c.complainant_type,
        complainant_name=c.complainant_name,
        status=c.status,
        priority=c.priority,
        received_date=c.received_date,
        due_date=c.due_date,
        disposed_date=c.disposed_date,
        is_overlapping=c.is_overlapping,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.post("/{complaint_id}/transition", response_model=ComplaintOut)
async def transition_status(
    complaint_id: UUID,
    transition_data: StatusTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("COMPLAINT_STATUS")),
):
    complaint = await transition_complaint_status(
        db,
        complaint_id=complaint_id,
        transition=transition_data,
        user_id=current_user.id,
        is_superuser=current_user.is_superuser,
    )
    await record_audit_log(
        db,
        action="STATUS_TRANSITION",
        entity_type="COMPLAINT",
        entity_id=complaint.id,
        user_id=current_user.id,
        changes={"new_status": transition_data.new_status.value, "remarks": transition_data.remarks}
    )
    await db.commit()

    c = await get_complaint_by_id(db, complaint.id)
    return ComplaintOut(
        id=c.id,
        complaint_number=c.complaint_number,
        institution_id=c.institution_id,
        institution_name=c.institution.name if c.institution else None,
        aicte_permanent_id=c.institution.aicte_permanent_id if c.institution else None,
        bureau_id=c.bureau_id,
        bureau_name=c.bureau.name if c.bureau else None,
        bureau_code=c.bureau.code if c.bureau else None,
        source_system_id=c.source_system_id,
        source_system_name=c.source_system.name if c.source_system else None,
        category_id=c.category_id,
        category_name=c.category.name if c.category else None,
        title=c.title,
        description=c.description,
        complainant_type=c.complainant_type,
        complainant_name=c.complainant_name,
        status=c.status,
        priority=c.priority,
        received_date=c.received_date,
        due_date=c.due_date,
        disposed_date=c.disposed_date,
        is_overlapping=c.is_overlapping,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.post("/{complaint_id}/assign")
async def assign_officer(
    complaint_id: UUID,
    officer_id: UUID,
    role_description: str = "Lead Investigator",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("COMPLAINT_ASSIGN")),
):
    assignment = await assign_complaint_officer(
        db,
        complaint_id=complaint_id,
        officer_id=officer_id,
        assigned_by_id=current_user.id,
        role_description=role_description,
    )
    await record_audit_log(
        db,
        action="ASSIGN_OFFICER",
        entity_type="COMPLAINT",
        entity_id=complaint_id,
        user_id=current_user.id,
        changes={"officer_id": str(officer_id), "role": role_description}
    )
    await db.commit()
    return {"message": "Officer assigned successfully.", "assignment_id": assignment.id}


@router.post("/{complaint_id}/triage")
async def trigger_triage(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await orchestrator.run_triage_pipeline(db, complaint_id)
    return result
