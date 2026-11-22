from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp_servers.runtime import MCPToolDefinition, mcp_runtime
from app.models.ai_agent import ApprovalRequest
from app.models.auth import User
from app.models.notification import Notification

NOTIFICATION_SERVER_NAME = "notification_mcp_server"
mcp_runtime.register_server(NOTIFICATION_SERVER_NAME)


async def get_pending_alerts(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    if not user:
        return {"alerts": []}

    query = select(Notification).where(Notification.user_id == user.id, Notification.is_read == False).limit(10)
    notes = (await db.execute(query)).scalars().all()
    return {
        "alerts": [
            {
                "id": str(n.id),
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "created_at": n.created_at.isoformat(),
            }
            for n in notes
        ]
    }


async def create_approval_request(db: AsyncSession, args: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
    req_type = args.get("request_type", "GENERIC_APPROVAL")
    ref_id_str = args.get("reference_id")
    payload = args.get("payload", {})

    ref_id = UUID(ref_id_str) if ref_id_str else user.id

    approval = ApprovalRequest(
        request_type=req_type,
        reference_id=ref_id,
        requested_by_id=user.id if user else None,
        payload=payload,
        status="PENDING",
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)

    return {
        "approval_request_id": str(approval.id),
        "status": "PENDING",
        "message": "Human approval request submitted to authorized officer.",
    }


mcp_runtime.register_tool(
    NOTIFICATION_SERVER_NAME,
    MCPToolDefinition(
        name="get_pending_alerts",
        description="Query unread coordination notifications, overlap alerts, and SLA warnings.",
        input_schema={"type": "object", "properties": {}},
        handler=get_pending_alerts,
        is_read_only=True,
    ),
)

mcp_runtime.register_tool(
    NOTIFICATION_SERVER_NAME,
    MCPToolDefinition(
        name="create_approval_request",
        description="Create a human-in-the-loop approval request for sensitive case decisions.",
        input_schema={
            "type": "object",
            "properties": {
                "request_type": {"type": "string"},
                "reference_id": {"type": "string"},
                "payload": {"type": "object"},
            },
            "required": ["request_type", "reference_id"],
        },
        handler=create_approval_request,
        is_read_only=False,  # Mutating operation
    ),
)

