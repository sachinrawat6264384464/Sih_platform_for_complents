from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.auth import User
from app.models.notification import Notification, NotificationPreference
from app.schemas.notification import NotificationOut, NotificationPreferenceOut, NotificationPreferenceUpdate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationOut])
async def get_my_notifications(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    notes = (await db.execute(query)).scalars().all()
    return notes


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = (
        await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    note.is_read = True
    await db.commit()
    return {"message": "Notification marked as read."}


@router.get("/preferences", response_model=NotificationPreferenceOut)
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == current_user.id))).scalar_one_or_none()
    if not pref:
        pref = NotificationPreference(user_id=current_user.id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref


@router.put("/preferences", response_model=NotificationPreferenceOut)
async def update_preferences(
    data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = (await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == current_user.id))).scalar_one_or_none()
    if not pref:
        pref = NotificationPreference(user_id=current_user.id)
        db.add(pref)
        await db.flush()

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(pref, k, v)

    await db.commit()
    await db.refresh(pref)
    return pref

