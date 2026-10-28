import json

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.mysql import get_session, USE_SQLITE

router = APIRouter()


class TrainingLogRequest(BaseModel):
    plan_id: int
    duration_actual: int


@router.post("", summary="记录训练")
async def log_training(req: TrainingLogRequest, user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await session.execute(
        text("INSERT INTO training_log (user_id, plan_id, duration_actual, completed) VALUES (:uid, :pid, :dur, 1)"),
        {"uid": user["user_id"], "pid": req.plan_id, "dur": req.duration_actual},
    )
    await session.commit()
    return {"logged": True}


@router.get("/stats", summary="训练统计")
async def training_stats(period: str = Query("week"), user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    days = 7 if period == "week" else 30

    if USE_SQLITE:
        sql = (
            "SELECT DATE(created_at) as date, COUNT(*) as count, SUM(duration_actual) as total_duration "
            "FROM training_log WHERE user_id = :uid AND created_at >= datetime('now', 'localtime', :days_str) "
            "GROUP BY DATE(created_at) ORDER BY date"
        )
        rows = await session.execute(text(sql), {"uid": user["user_id"], "days_str": f"-{days} days"})
    else:
        sql = (
            "SELECT DATE(created_at) as date, COUNT(*) as count, SUM(duration_actual) as total_duration "
            "FROM training_log WHERE user_id = :uid AND created_at >= DATE_SUB(NOW(), INTERVAL :days DAY) "
            "GROUP BY DATE(created_at) ORDER BY date"
        )
        rows = await session.execute(text(sql), {"uid": user["user_id"], "days": days})

    items = [{"date": str(r.date), "count": r.count, "total_duration": r.total_duration or 0} for r in rows]

    total = sum(item["count"] for item in items)
    total_duration = sum(item["total_duration"] for item in items)
    return {"period": period, "items": items, "total_count": total, "total_duration": total_duration}


@router.get("/streak", summary="连续打卡天数")
async def streak_days(user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rows = await session.execute(
        text("SELECT DISTINCT DATE(created_at) as date FROM training_log WHERE user_id = :uid ORDER BY date DESC LIMIT 365"),
        {"uid": user["user_id"]},
    )
    dates = [str(r.date) for r in rows]
    if not dates:
        return {"streak": 0}

    from datetime import date, timedelta
    today = date.today()
    streak = 0
    check_date = today
    for d_str in dates:
        d = date.fromisoformat(d_str)
        if d == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        elif d == check_date + timedelta(days=1):
            continue
        else:
            break
    return {"streak": streak}