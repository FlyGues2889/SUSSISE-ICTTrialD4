import json
import os
import sys

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.mysql import get_session

router = APIRouter()

SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "skills")
if SKILLS_PATH not in sys.path:
    sys.path.insert(0, SKILLS_PATH)
from plan_matcher import match_plans


@router.get("/recommend", summary="推荐运动方案")
async def recommend_plans(
    area: str = Query(..., description="部位: neck/back/full"),
    duration: int = Query(..., description="时长(分钟): 3/5/10/15"),
    scene: str = Query(..., description="场景: desk/standing/home"),
    risk_level: str = Query("medium", description="风险等级: low/medium/high"),
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    rows = await session.execute(
        text(
            "SELECT plan_id, name, duration_min, target_area, scene, movements, suitable_level, contraindication, description "
            "FROM exercise_plan WHERE target_area IN (:area, 'full') AND duration_min = :duration AND scene = :scene"
        ),
        {"area": area, "duration": duration, "scene": scene},
    )
    all_plans = []
    for r in rows:
        all_plans.append({
            "plan_id": r.plan_id,
            "name": r.name,
            "duration_min": r.duration_min,
            "target_area": r.target_area,
            "scene": r.scene,
            "movements": json.loads(r.movements) if r.movements else [],
            "suitable_level": r.suitable_level or "",
            "contraindication": r.contraindication or "",
            "description": r.description or "",
        })

    recommended = match_plans(all_plans, risk_level, area, duration, scene)
    return {"plans": recommended}


@router.get("/{plan_id}", summary="方案详情")
async def get_plan(plan_id: int, session: AsyncSession = Depends(get_session)):
    row = await session.execute(
        text(
            "SELECT plan_id, name, duration_min, target_area, scene, movements, suitable_level, contraindication, description "
            "FROM exercise_plan WHERE plan_id = :pid"
        ),
        {"pid": plan_id},
    )
    r = row.first()
    if not r:
        return {"error": "方案不存在"}
    return {
        "plan_id": r.plan_id,
        "name": r.name,
        "duration_min": r.duration_min,
        "target_area": r.target_area,
        "scene": r.scene,
        "movements": json.loads(r.movements) if r.movements else [],
        "suitable_level": r.suitable_level or "",
        "contraindication": r.contraindication or "",
        "description": r.description or "",
    }


@router.get("", summary="方案列表")
async def list_plans(
    area: str | None = Query(None),
    duration: int | None = Query(None),
    scene: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    conditions = []
    params = {}
    if area:
        conditions.append("target_area = :area")
        params["area"] = area
    if duration:
        conditions.append("duration_min = :duration")
        params["duration"] = duration
    if scene:
        conditions.append("scene = :scene")
        params["scene"] = scene

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    rows = await session.execute(
        text(f"SELECT plan_id, name, duration_min, target_area, scene, description FROM exercise_plan{where_clause} ORDER BY plan_id"),
        params,
    )
    items = [
        {"plan_id": r.plan_id, "name": r.name, "duration_min": r.duration_min, "target_area": r.target_area, "scene": r.scene, "description": r.description or ""}
        for r in rows
    ]
    return {"items": items}