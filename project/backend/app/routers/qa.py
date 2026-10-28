import json
import os
import sys

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.mysql import get_session

router = APIRouter()

SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "skills")
if SKILLS_PATH not in sys.path:
    sys.path.insert(0, SKILLS_PATH)
from qa_responder import respond_qa


class QARequest(BaseModel):
    question: str


@router.post("", summary="智能问答")
async def ask_question(req: QARequest, user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    rows = await session.execute(
        text("SELECT kb_id, question, answer, keywords, related_plans, category FROM knowledge_base")
    )
    kb_items = []
    for r in rows:
        kb_items.append({
            "kb_id": r.kb_id,
            "question": r.question,
            "answer": r.answer,
            "keywords": r.keywords or "",
            "related_plans": json.loads(r.related_plans) if r.related_plans else [],
            "category": r.category or "",
        })

    result = respond_qa(req.question, kb_items)
    return result