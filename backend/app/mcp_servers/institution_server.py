from typing import Any, Dict, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.mcp_servers.runtime import MCPToolDefinition, mcp_runtime
from app.models.auth import User
from app.models.complaint import Complaint
from app.models.institution import Institution

INSTITUTION_SERVER_NAME = "institution_mcp_server"
mcp_runtime.register_server(INSTITUTION_SERVER_NAME)


async def search_institution(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    query_str = args.get("query", "").strip()
    if not query_str:
        return {"items": []}

    stmt = (
        select(Institution)
        .options(selectinload(Institution.aliases), selectinload(Institution.regional_office))
        .where(
            or_(
                Institution.name.ilike(f"%{query_str}%"),
                Institution.aicte_permanent_id.ilike(f"%{query_str}%"),
                Institution.city.ilike(f"%{query_str}%"),
            )
        )
        .limit(10)
    )
    institutions = (await db.execute(stmt)).scalars().all()

    return {
        "items": [
            {
                "id": str(i.id),
                "aicte_permanent_id": i.aicte_permanent_id,
                "name": i.name,
                "city": i.city,
                "district": i.district,
                "state": i.state,
                "institution_type": i.institution_type,
                "approval_status": i.approval_status,
                "regional_office": i.regional_office.name if i.regional_office else "",
            }
            for i in institutions
        ]
    }


async def get_institution_profile(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    perm_id = args.get("aicte_permanent_id")
    inst = (
        await db.execute(
            select(Institution)
            .options(selectinload(Institution.aliases), selectinload(Institution.identifiers), selectinload(Institution.regional_office))
            .where(Institution.aicte_permanent_id == perm_id)
        )
    ).scalar_one_or_none()

    if not inst:
        return {"error": f"Institution Permanent ID '{perm_id}' not found."}

    # Fetch complaint count
    c_count = (await db.execute(select(Complaint).where(Complaint.institution_id == inst.id))).scalars().all()

    return {
        "aicte_permanent_id": inst.aicte_permanent_id,
        "name": inst.name,
        "type": inst.institution_type,
        "address": f"{inst.address}, {inst.city}, {inst.district}, {inst.state} - {inst.pincode or ''}",
        "approval_status": inst.approval_status,
        "regional_office": inst.regional_office.name if inst.regional_office else "",
        "total_complaints_on_record": len(c_count),
        "aliases": [a.alias_name for a in inst.aliases],
    }


mcp_runtime.register_tool(
    INSTITUTION_SERVER_NAME,
    MCPToolDefinition(
        name="search_institution",
        description="Search institutions by AICTE Permanent ID, name, or geographic city.",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        handler=search_institution,
        is_read_only=True,
    ),
)

mcp_runtime.register_tool(
    INSTITUTION_SERVER_NAME,
    MCPToolDefinition(
        name="get_institution_profile",
        description="Fetch verified AICTE institutional dossier, approval credentials, aliases, and complaint history count.",
        input_schema={"type": "object", "properties": {"aicte_permanent_id": {"type": "string"}}, "required": ["aicte_permanent_id"]},
        handler=get_institution_profile,
        is_read_only=True,
    ),
)

