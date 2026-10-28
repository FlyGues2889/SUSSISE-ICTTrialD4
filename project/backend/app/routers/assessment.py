import json
import os
import sys

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.mysql import get_session

router = APIRouter()

SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "skills")
if SKILLS_PATH not in sys.path:
    sys.path.insert(0, SKILLS_PATH)
from posture_assessment import assess_posture
from safety_check import check_safety


class AssessmentSubmitRequest(BaseModel):
    area: str
    answers: dict


@router.post("", summary="提交体态评估")
async def submit_assessment(req: AssessmentSubmitRequest, user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = assess_posture(req.area, req.answers)

    safety = check_safety(result["risk_level"], result.get("red_line_hit", False), user.get("age"), user.get("history"))

    await session.execute(
        text(
            "INSERT INTO assessment (user_id, area, answers, total_score, risk_level, problem_points, suggestion, need_medical) "
            "VALUES (:user_id, :area, :answers, :total_score, :risk_level, :problem_points, :suggestion, :need_medical)"
        ),
        {
            "user_id": user["user_id"],
            "area": req.area,
            "answers": json.dumps(req.answers),
            "total_score": result["total_score"],
            "risk_level": result["risk_level"],
            "problem_points": json.dumps(result["problem_points"], ensure_ascii=False),
            "suggestion": result["suggestion"],
            "need_medical": safety["need_medical"],
        },
    )
    await session.commit()

    return {
        "risk_level": result["risk_level"],
        "total_score": result["total_score"],
        "problem_points": result["problem_points"],
        "suggestion": result["suggestion"],
        "need_medical": safety["need_medical"],
        "safety_message": safety.get("message", ""),
    }


@router.get("/history", summary="评估历史")
async def assessment_history(user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rows = await session.execute(
        text(
            "SELECT assessment_id, area, risk_level, total_score, problem_points, suggestion, need_medical, created_at "
            "FROM assessment WHERE user_id = :uid ORDER BY created_at DESC"
        ),
        {"uid": user["user_id"]},
    )
    items = []
    for r in rows:
        items.append({
            "assessment_id": r.assessment_id,
            "area": r.area,
            "risk_level": r.risk_level,
            "total_score": r.total_score,
            "problem_points": json.loads(r.problem_points) if r.problem_points else [],
            "suggestion": r.suggestion,
            "need_medical": bool(r.need_medical),
            "created_at": str(r.created_at),
        })
    return {"items": items}