from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.ai_agent import AgentRun, AgentStep, ApprovalRequest
from app.models.auth import User
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/agents", tags=["Agentic AI & Human-in-the-Loop"])


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    remarks: str


@router.get("/runs")
async def get_agent_runs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(AgentRun)
        .options(selectinload(AgentRun.steps))
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
    )
    runs = (await db.execute(query)).scalars().all()
    return [
        {
            "id": r.id,
            "agent_name": r.agent_name,
            "workflow_id": r.workflow_id,
            "status": r.status,
            "duration_ms": r.duration_ms,
            "steps_count": len(r.steps),
            "created_at": r.created_at.isoformat(),
            "input_state": r.input_state,
            "output_state": r.output_state,
            "steps": [
                {
                    "step_number": s.step_number,
                    "node_name": s.node_name,
                    "reasoning_trace": s.reasoning_trace,
                }
                for s in r.steps
            ]
        }
        for r in runs
    ]


@router.get("/approvals")
async def get_approval_requests(
    status_filter: Optional[str] = Query("PENDING"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())
    if status_filter:
        query = query.where(ApprovalRequest.status == status_filter)
    approvals = (await db.execute(query)).scalars().all()

    return [
        {
            "id": a.id,
            "request_type": a.request_type,
            "reference_id": a.reference_id,
            "status": a.status,
            "payload": a.payload,
            "reviewer_remarks": a.reviewer_remarks,
            "created_at": a.created_at.isoformat(),
        }
        for a in approvals
    ]


@router.post("/approvals/{approval_id}/decide")
async def decide_approval_request(
    approval_id: UUID,
    decision: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("OVERLAP_REVIEW")),
):
    req = (await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))).scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

    req.status = "APPROVED" if decision.approved else "REJECTED"
    req.reviewed_by_id = current_user.id
    req.reviewer_remarks = decision.remarks

    await record_audit_log(
        db,
        action="DECIDE_APPROVAL",
        entity_type="APPROVAL_REQUEST",
        entity_id=approval_id,
        user_id=current_user.id,
        changes={"status": req.status, "remarks": decision.remarks}
    )
    await db.commit()

    return {"message": f"Approval request marked as '{req.status}'."}
