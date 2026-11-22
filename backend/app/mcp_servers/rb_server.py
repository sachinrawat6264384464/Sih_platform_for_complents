from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.mcp_servers.runtime import MCPToolDefinition, mcp_runtime
from app.models.auth import User
from app.models.bureau import Bureau
from app.models.case import Case, CaseAction
from app.models.complaint import Complaint

RB_SERVER_NAME = "regulation_bureau_mcp_server"
mcp_runtime.register_server(RB_SERVER_NAME)


async def get_rb_cases(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    limit = args.get("limit", 10)
    rb_bureau = (await db.execute(select(Bureau).where(Bureau.code == "RB"))).scalar_one_or_none()
    if not rb_bureau:
        return {"items": [], "total": 0}

    query = (
        select(Case)
        .options(selectinload(Case.institution), selectinload(Case.actions))
        .where(Case.bureau_id == rb_bureau.id)
        .order_by(Case.created_at.desc())
        .limit(limit)
    )
    cases = (await db.execute(query)).scalars().all()

    return {
        "items": [
            {
                "case_number": c.case_number,
                "institution_name": c.institution.name if c.institution else "",
                "title": c.title,
                "current_status": c.current_status,
                "actions_count": len(c.actions),
            }
            for c in cases
        ],
        "total": len(cases),
    }


async def get_regulatory_actions(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    case_number = args.get("case_number")
    c = (
        await db.execute(
            select(Case)
            .options(selectinload(Case.actions))
            .where(Case.case_number == case_number)
        )
    ).scalar_one_or_none()

    if not c:
        return {"error": f"Case '{case_number}' not found in Regulation Bureau."}

    return {
        "case_number": c.case_number,
        "actions": [
            {
                "type": a.action_type,
                "title": a.action_title,
                "details": a.action_details,
                "action_date": a.action_date.isoformat(),
            }
            for a in c.actions
        ],
    }


mcp_runtime.register_tool(
    RB_SERVER_NAME,
    MCPToolDefinition(
        name="get_rb_cases",
        description="Query active regulatory inquiry cases, show-cause proceedings, and disciplinary dossiers.",
        input_schema={"type": "object", "properties": {"limit": {"type": "integer", "default": 10}}},
        handler=get_rb_cases,
        is_read_only=True,
    ),
)

mcp_runtime.register_tool(
    RB_SERVER_NAME,
    MCPToolDefinition(
        name="get_regulatory_actions",
        description="Retrieve all regulatory notices, inspections, hearings, and penalties issued on a case.",
        input_schema={"type": "object", "properties": {"case_number": {"type": "string"}}, "required": ["case_number"]},
        handler=get_regulatory_actions,
        is_read_only=True,
    ),
)

