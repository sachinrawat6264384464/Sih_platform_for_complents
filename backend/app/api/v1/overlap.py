from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.auth import User
from app.models.complaint import Complaint
from app.models.institution import Institution
from app.models.overlap import OverlapCandidate, OverlapReview
from app.schemas.overlap import (
    OverlapCandidateListResponse,
    OverlapCandidateOut,
    OverlapReviewRequest,
    OverlapStageBreakdown,
)
from app.services.audit_service import record_audit_log
from app.services.overlap_engine import scan_complaint_for_overlaps

router = APIRouter(prefix="/overlap", tags=["Overlap Detection & Coordination"])


@router.get("", response_model=OverlapCandidateListResponse)
async def get_overlap_candidates(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(OverlapCandidate)
        .options(
            selectinload(OverlapCandidate.complaint_a).selectinload(Complaint.bureau),
            selectinload(OverlapCandidate.complaint_b).selectinload(Complaint.bureau),
            selectinload(OverlapCandidate.institution),
        )
        .order_by(OverlapCandidate.total_confidence_score.desc())
    )
    if status_filter:
        query = query.where(OverlapCandidate.status == status_filter)

    candidates = (await db.execute(query)).scalars().all()

    items = []
    for c in candidates:
        breakdown = OverlapStageBreakdown(
            exact_id=c.stage1_exact_id_score,
            name_fuzzy=c.stage2_name_fuzzy_score,
            geo_proximity=c.stage3_geo_score,
            category_match=c.stage4_category_score,
            bm25_text=c.stage5_bm25_score,
            vector_similarity=c.stage6_vector_score,
            cross_bureau=c.stage7_bureau_score,
        )
        items.append(
            OverlapCandidateOut(
                id=c.id,
                complaint_a_id=c.complaint_a_id,
                complaint_a_number=c.complaint_a.complaint_number if c.complaint_a else "",
                complaint_a_title=c.complaint_a.title if c.complaint_a else "",
                complaint_a_bureau=c.complaint_a.bureau.code if c.complaint_a and c.complaint_a.bureau else "",
                complaint_b_id=c.complaint_b_id,
                complaint_b_number=c.complaint_b.complaint_number if c.complaint_b else "",
                complaint_b_title=c.complaint_b.title if c.complaint_b else "",
                complaint_b_bureau=c.complaint_b.bureau.code if c.complaint_b and c.complaint_b.bureau else "",
                institution_id=c.institution_id,
                institution_name=c.institution.name if c.institution else "",
                aicte_permanent_id=c.institution.aicte_permanent_id if c.institution else "",
                total_confidence_score=c.total_confidence_score,
                stage_scores=breakdown,
                match_reasons=c.match_reasons if isinstance(c.match_reasons, list) else [],
                status=c.status,
                created_at=c.created_at,
            )
        )

    pending_count = (await db.execute(select(func.count(OverlapCandidate.id)).where(OverlapCandidate.status == "Pending"))).scalar_one()
    confirmed_count = (await db.execute(select(func.count(OverlapCandidate.id)).where(OverlapCandidate.status == "Confirmed"))).scalar_one()

    return {
        "items": items,
        "total": len(items),
        "pending_count": pending_count,
        "confirmed_count": confirmed_count,
    }


@router.post("/{candidate_id}/review")
async def review_overlap(
    candidate_id: UUID,
    review_data: OverlapReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("OVERLAP_REVIEW")),
):
    candidate = (await db.execute(select(OverlapCandidate).where(OverlapCandidate.id == candidate_id))).scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Overlap candidate record not found.")

    valid_verdicts = ["Confirmed", "False_Positive", "Linked"]
    if review_data.verdict not in valid_verdicts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Verdict must be one of {valid_verdicts}")

    candidate.status = review_data.verdict

    review = OverlapReview(
        overlap_candidate_id=candidate.id,
        reviewer_id=current_user.id,
        verdict=review_data.verdict,
        remarks=review_data.remarks,
    )
    db.add(review)

    await record_audit_log(
        db,
        action="OVERLAP_REVIEW",
        entity_type="OVERLAP_CANDIDATE",
        entity_id=candidate.id,
        user_id=current_user.id,
        changes={"verdict": review_data.verdict, "remarks": review_data.remarks}
    )
    await db.commit()

    return {"message": f"Overlap candidate reviewed as '{review_data.verdict}'."}


@router.post("/scan/{complaint_id}")
async def trigger_overlap_scan(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidates = await scan_complaint_for_overlaps(db, complaint_id)
    return {"message": f"Scan completed. Found {len(candidates)} new overlap candidates.", "candidates_count": len(candidates)}
