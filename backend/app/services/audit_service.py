from typing import Any, Dict, Optional
from uuid import UUID
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog, SecurityEvent


async def record_audit_log(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    changes: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AuditLog:
    ip_addr = request.client.host if request and request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "")[:250] if request else "SYSTEM"

    audit = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        changes=changes,
        ip_address=ip_addr,
        user_agent=ua
    )
    db.add(audit)
    await db.flush()
    return audit


async def record_security_event(
    db: AsyncSession,
    event_type: str,
    details: Dict[str, Any],
    request: Optional[Request] = None
) -> SecurityEvent:
    ip_addr = request.client.host if request and request.client else "127.0.0.1"

    sec_event = SecurityEvent(
        event_type=event_type,
        ip_address=ip_addr,
        details=details
    )
    db.add(sec_event)
    await db.flush()
    return sec_event
