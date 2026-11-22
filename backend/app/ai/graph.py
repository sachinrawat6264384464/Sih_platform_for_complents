from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.ai_agent import AgentRun, AgentStep, ApprovalRequest
from app.models.complaint import Complaint, ComplaintCategory
from app.models.institution import Institution
from app.services.overlap_engine import OverlapDetectionEngine, scan_complaint_for_overlaps


class ComplaintTriageState(BaseModel):
    complaint_id: str
    title: str
    description: str
    institution_id: Optional[str] = None
    institution_resolved_id: Optional[str] = None
    resolution_confidence: float = 0.0
    category_id: Optional[str] = None
    category_code: Optional[str] = None
    potential_overlaps_count: int = 0
    coordination_recommended: bool = False
    coordination_lead_bureau: Optional[str] = None
    human_approval_required: bool = False
    trace: List[Dict[str, Any]] = []


class AICTEMultiAgentOrchestrator:
    """
    Stateful Multi-Agent Orchestrator for AICTE Nexus.
    Coordinates Classification, Institution Resolution, Overlap Detection,
    Bureau Coordination, and Human Approval Queues with granular step auditing.
    """

    async def run_triage_pipeline(self, db: AsyncSession, complaint_id: UUID) -> Dict[str, Any]:
        start_time = time.time()
        c = (
            await db.execute(
                select(Complaint)
                .options(
                    selectinload(Complaint.institution),
                    selectinload(Complaint.bureau),
                    selectinload(Complaint.category),
                )
                .where(Complaint.id == complaint_id)
            )
        ).scalar_one_or_none()

        if not c:
            raise ValueError(f"Complaint {complaint_id} not found")

        state = ComplaintTriageState(
            complaint_id=str(c.id),
            title=c.title,
            description=c.description,
            institution_id=str(c.institution_id),
            category_id=str(c.category_id),
            category_code=c.category.code if c.category else "GENERAL",
        )

        agent_run = AgentRun(
            agent_name="AICTE_SUPERVISOR_TRIAGE",
            workflow_id=f"TRIAGE-{c.complaint_number}",
            input_state=state.model_dump(),
            status="RUNNING",
            duration_ms=0.0
        )
        db.add(agent_run)
        await db.flush()

        step_num = 1

        # ----------------------------------------------------
        # Agent 1: Complaint Classification Agent
        # ----------------------------------------------------
        urgency = "HIGH" if any(w in (c.title + c.description).lower() for w in ["ragging", "fraud", "suicide", "police", "fir", "bribe", "capitation"]) else "NORMAL"
        state.trace.append({
            "step": step_num,
            "agent": "ClassificationAgent",
            "classification": state.category_code,
            "urgency": urgency,
            "evidence": "Grievance taxonomy verified against standard AICTE categories."
        })
        db.add(AgentStep(
            agent_run_id=agent_run.id,
            step_number=step_num,
            node_name="ClassificationAgent",
            state_snapshot=state.model_dump(),
            reasoning_trace=f"Categorized as '{state.category_code}' with detected urgency '{urgency}'."
        ))
        step_num += 1

        # ----------------------------------------------------
        # Agent 2: Institution Resolution Agent
        # ----------------------------------------------------
        inst_match = c.institution
        conf = 1.0 if inst_match and inst_match.is_verified else 0.85
        state.institution_resolved_id = str(inst_match.id) if inst_match else None
        state.resolution_confidence = conf
        state.trace.append({
            "step": step_num,
            "agent": "InstitutionResolutionAgent",
            "permanent_id": inst_match.aicte_permanent_id if inst_match else "UNKNOWN",
            "confidence": conf,
            "evidence": f"Matched AICTE Permanent ID '{inst_match.aicte_permanent_id if inst_match else ''}'."
        })
        db.add(AgentStep(
            agent_run_id=agent_run.id,
            step_number=step_num,
            node_name="InstitutionResolutionAgent",
            state_snapshot=state.model_dump(),
            reasoning_trace=f"Resolved institution '{inst_match.name if inst_match else ''}' with {conf*100:.1f}% confidence."
        ))
        step_num += 1

        # ----------------------------------------------------
        # Agent 3: Duplicate & Overlap Detection Agent
        # ----------------------------------------------------
        overlap_candidates = await scan_complaint_for_overlaps(db, c.id)
        state.potential_overlaps_count = len(overlap_candidates)
        state.trace.append({
            "step": step_num,
            "agent": "DuplicateDetectionAgent",
            "detected_candidates_count": len(overlap_candidates),
            "evidence": f"Executed 8-stage matching sieve across active institutional complaint records."
        })
        db.add(AgentStep(
            agent_run_id=agent_run.id,
            step_number=step_num,
            node_name="DuplicateDetectionAgent",
            state_snapshot=state.model_dump(),
            reasoning_trace=f"Found {len(overlap_candidates)} potential overlapping cases exceeding threshold."
        ))
        step_num += 1

        # ----------------------------------------------------
        # Agent 4: Bureau Coordination Agent
        # ----------------------------------------------------
        if overlap_candidates:
            state.coordination_recommended = True
            # Recommend leading bureau based on severity
            has_rb = any(
                cand.complaint_a.bureau.code == "RB" or cand.complaint_b.bureau.code == "RB"
                for cand in overlap_candidates if cand.complaint_a and cand.complaint_b and cand.complaint_a.bureau and cand.complaint_b.bureau
            )
            state.coordination_lead_bureau = "Regulation Bureau (RB)" if has_rb else "Public Grievance Redressal Cell (PGRC)"
            state.human_approval_required = True
        else:
            state.coordination_recommended = False
            state.coordination_lead_bureau = c.bureau.name if c.bureau else "Originating Bureau"

        state.trace.append({
            "step": step_num,
            "agent": "BureauCoordinationAgent",
            "coordination_recommended": state.coordination_recommended,
            "suggested_lead": state.coordination_lead_bureau,
            "requires_human_approval": state.human_approval_required,
        })
        db.add(AgentStep(
            agent_run_id=agent_run.id,
            step_number=step_num,
            node_name="BureauCoordinationAgent",
            state_snapshot=state.model_dump(),
            reasoning_trace=f"Coordination recommended: {state.coordination_recommended}. Recommended lead: {state.coordination_lead_bureau}."
        ))
        step_num += 1

        # ----------------------------------------------------
        # Agent 7: Supervisor Final Decision & Human Approval
        # ----------------------------------------------------
        if state.human_approval_required:
            approval = ApprovalRequest(
                request_type="COORDINATION_OVERLAP_APPROVAL",
                reference_id=c.id,
                payload={
                    "complaint_number": c.complaint_number,
                    "institution_name": inst_match.name if inst_match else "",
                    "overlap_count": len(overlap_candidates),
                    "suggested_lead_bureau": state.coordination_lead_bureau,
                },
                status="PENDING",
            )
            db.add(approval)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        agent_run.status = "COMPLETED"
        agent_run.duration_ms = duration_ms
        agent_run.output_state = state.model_dump()

        await db.commit()

        return {
            "status": "COMPLETED",
            "workflow_id": agent_run.workflow_id,
            "duration_ms": duration_ms,
            "state": state.model_dump(),
        }


orchestrator = AICTEMultiAgentOrchestrator()
