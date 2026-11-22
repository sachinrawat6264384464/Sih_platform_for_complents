from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.mcp_servers.runtime import MCPToolDefinition, mcp_runtime
from app.models.auth import User
from app.models.bureau import Bureau
from app.models.complaint import Complaint, ComplaintStatus

PGRC_SERVER_NAME = "pgrc_mcp_server"
mcp_runtime.register_server(PGRC_SERVER_NAME)


async def get_pgrc_complaints(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    limit = args.get("limit", 10)
    pgrc_bureau = (await db.execute(select(Bureau).where(Bureau.code == "PGRC"))).scalar_one_or_none()
    if not pgrc_bureau:
        return {"items": [], "total": 0}

    query = (
        select(Complaint)
        .options(selectinload(Complaint.institution), selectinload(Complaint.category))
        .where(Complaint.bureau_id == pgrc_bureau.id)
        .order_by(Complaint.created_at.desc())
        .limit(limit)
    )
    complaints = (await db.execute(query)).scalars().all()

    return {
        "items": [
            {
                "complaint_number": c.complaint_number,
                "institution_name": c.institution.name if c.institution else "",
                "aicte_permanent_id": c.institution.aicte_permanent_id if c.institution else "",
                "title": c.title,
                "status": c.status.value,
                "received_date": c.received_date.isoformat(),
            }
            for c in complaints
        ],
        "total": len(complaints),
    }


async def get_pgrc_complaint_details(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    complaint_no = args.get("complaint_number")
    c = (
        await db.execute(
            select(Complaint)
            .options(selectinload(Complaint.institution), selectinload(Complaint.category), selectinload(Complaint.status_history))
            .where(Complaint.complaint_number == complaint_no)
        )
    ).scalar_one_or_none()

    if not c:
        return {"error": f"Complaint '{complaint_no}' not found in PGRC"}

    return {
        "complaint_number": c.complaint_number,
        "institution_name": c.institution.name if c.institution else "",
        "category": c.category.name if c.category else "",
        "title": c.title,
        "description": c.description,
        "status": c.status.value,
        "history": [
            {"status": h.new_status, "remarks": h.remarks, "timestamp": h.created_at.isoformat()}
            for h in c.status_history
        ],
    }


mcp_runtime.register_tool(
    PGRC_SERVER_NAME,
    MCPToolDefinition(
        name="get_pgrc_complaints",
        description="Fetch list of recent Public Grievance Redressal Cell (PGRC) complaints.",
        input_schema={"type": "object", "properties": {"limit": {"type": "integer", "default": 10}}},
        handler=get_pgrc_complaints,
        is_read_only=True,
    ),
)

mcp_runtime.register_tool(
    PGRC_SERVER_NAME,
    MCPToolDefinition(
        name="get_pgrc_complaint_details",
        description="Retrieve full dossier, chronological remarks, and status for a PGRC complaint number.",
        input_schema={"type": "object", "properties": {"complaint_number": {"type": "string"}}, "required": ["complaint_number"]},
        handler=get_pgrc_complaint_details,
        is_read_only=True,
    ),
)

