from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.mysql import get_session

router = APIRouter()


class ReminderRequest(BaseModel):
    interval_min: int = 45
    active_hours: str = "09:00-18:00"
    enabled: bool = True


@router.put("", summary="设置提醒")
async def set_reminder(req: ReminderRequest, user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    existing = await session.execute(
        text("SELECT reminder_id FROM reminder_setting WHERE user_id = :uid"),
        {"uid": user["user_id"]},
    )
    if existing.first():
        await session.execute(
            text("UPDATE reminder_setting SET interval_min = :interval, active_hours = :hours, enabled = :enabled WHERE user_id = :uid"),
            {"interval": req.interval_min, "hours": req.active_hours, "enabled": req.enabled, "uid": user["user_id"]},
        )
    else:
        await session.execute(
            text("INSERT INTO reminder_setting (user_id, interval_min, active_hours, enabled) VALUES (:uid, :interval, :hours, :enabled)"),
            {"uid": user["user_id"], "interval": req.interval_min, "hours": req.active_hours, "enabled": req.enabled},
        )
    await session.commit()
    return {"saved": True}


@router.get("", summary="查询提醒设置")
async def get_reminder(user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    row = await session.execute(
        text("SELECT interval_min, active_hours, enabled FROM reminder_setting WHERE user_id = :uid"),
        {"uid": user["user_id"]},
    )
    r = row.first()
    if not r:
        return {"interval_min": 45, "active_hours": "09:00-18:00", "enabled": True}
    return {"interval_min": r.interval_min, "active_hours": r.active_hours, "enabled": bool(r.enabled)}