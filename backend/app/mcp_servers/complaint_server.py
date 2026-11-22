from typing import Any, Dict, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.mcp_servers.runtime import MCPToolDefinition, mcp_runtime
from app.models.auth import User
from app.models.complaint import Complaint

COMPLAINT_SERVER_NAME = "complaint_mcp_server"
mcp_runtime.register_server(COMPLAINT_SERVER_NAME)


async def search_complaints(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    query_str = args.get("query", "").strip()
    limit = args.get("limit", 10)

    stmt = (
        select(Complaint)
        .options(selectinload(Complaint.institution), selectinload(Complaint.bureau), selectinload(Complaint.category))
        .where(
            or_(
                Complaint.complaint_number.ilike(f"%{query_str}%"),
                Complaint.title.ilike(f"%{query_str}%"),
                Complaint.description.ilike(f"%{query_str}%"),
            )
        )
        .limit(limit)
    )
    complaints = (await db.execute(stmt)).scalars().all()

    return {
        "items": [
            {
                "complaint_number": c.complaint_number,
                "institution": c.institution.name if c.institution else "",
                "bureau": c.bureau.code if c.bureau else "",
                "category": c.category.name if c.category else "",
                "title": c.title,
                "status": c.status.value,
                "is_overlapping": c.is_overlapping,
            }
            for c in complaints
        ]
    }


async def get_complaint_details(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    complaint_no = args.get("complaint_number")
    c = (
        await db.execute(
            select(Complaint)
            .options(
                selectinload(Complaint.institution),
                selectinload(Complaint.bureau),
                selectinload(Complaint.category),
                selectinload(Complaint.status_history),
                selectinload(Complaint.documents),
            )
            .where(Complaint.complaint_number == complaint_no)
        )
    ).scalar_one_or_none()

    if not c:
        return {"error": f"Complaint '{complaint_no}' not found."}

    return {
        "complaint_number": c.complaint_number,
        "institution_name": c.institution.name if c.institution else "",
        "bureau": c.bureau.name if c.bureau else "",
        "category": c.category.name if c.category else "",
        "title": c.title,
        "description": c.description,
        "status": c.status.value,
        "priority": c.priority.value,
        "received_date": c.received_date.isoformat(),
        "due_date": c.due_date.isoformat() if c.due_date else None,
        "history": [
            {"status": h.new_status, "remarks": h.remarks, "timestamp": h.created_at.isoformat()}
            for h in c.status_history
        ],
        "documents": [
            {"file_name": d.file_name, "type": d.document_type}
            for d in c.documents
        ]
    }


mcp_runtime.register_tool(
    COMPLAINT_SERVER_NAME,
    MCPToolDefinition(
        name="search_complaints",
        description="Search across all AICTE complaints by keywords, number, or subject matter.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}}, "required": ["query"]},
        handler=search_complaints,
        is_read_only=True,
    ),
)

mcp_runtime.register_tool(
    COMPLAINT_SERVER_NAME,
    MCPToolDefinition(
        name="get_complaint_details",
        description="Fetch detailed complaint record including chronological history and documents.",
        input_schema={"type": "object", "properties": {"complaint_number": {"type": "string"}}, "required": ["complaint_number"]},
        handler=get_complaint_details,
        is_read_only=True,
    ),
)
