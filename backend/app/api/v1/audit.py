from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.audit import AuditLog, SecurityEvent, SystemSetting
from app.models.auth import User
from app.schemas.audit import AuditLogOut, SecurityEventOut, SystemSettingOut

router = APIRouter(prefix="/audit", tags=["Audit & Security Logs"])


@router.get("/logs", response_model=List[AuditLogOut])
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("AUDIT_READ")),
):
    query = (
        select(AuditLog)
        .options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = (await db.execute(query)).scalars().all()
    return [
        AuditLogOut(
            id=l.id,
            user_id=l.user_id,
            user_name=l.user.full_name if l.user else "SYSTEM",
            action=l.action,
            entity_type=l.entity_type,
            entity_id=l.entity_id,
            changes=l.changes,
            ip_address=l.ip_address,
            user_agent=l.user_agent,
            created_at=l.created_at,
        )
        for l in logs
    ]


@router.get("/security", response_model=List[SecurityEventOut])
async def get_security_events(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("AUDIT_READ")),
):
    query = select(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(limit)
    events = (await db.execute(query)).scalars().all()
    return events


@router.get("/settings", response_model=List[SystemSettingOut])
async def get_settings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings_list = (await db.execute(select(SystemSetting).order_by(SystemSetting.setting_key))).scalars().all()
    return settings_list


@router.put("/settings/{setting_key}", response_model=SystemSettingOut)
async def update_setting(
    setting_key: str,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("SYSTEM_SETTINGS")),
):
    setting = (await db.execute(select(SystemSetting).where(SystemSetting.setting_key == setting_key))).scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting key not found")

    setting.setting_value = payload
    await db.commit()
    await db.refresh(setting)
    return setting
