import json
import hashlib
import os
import sys

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.mysql import get_session
from app.services import ai, cache

router = APIRouter()

SKILLS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "skills")
if SKILLS_PATH not in sys.path:
    sys.path.insert(0, SKILLS_PATH)
from qa_responder import respond_qa

LOCAL_CONFIDENCE_THRESHOLD = 0.25
LOCAL_CACHE_TTL = 3600
AI_CACHE_TTL = 1800


class QAHistoryItem(BaseModel):
    role: str
    content: str


class QARequest(BaseModel):
    question: str
    history: list[QAHistoryItem] | None = None


def _normalize_history(items) -> list[dict]:
    history = []
    for item in items or []:
        role = (item.role or "").strip()
        content = (item.content or "").strip()
        if role in ("user", "assistant") and content:
            history.append({"role": role, "content": content[:500]})
    return history[-4:]


def _cache_key(question: str, history: list[dict]) -> str:
    raw = question.lower() + "|" + "|".join(f"{h['role']}:{h['content']}" for h in history)
    return "qa:cache:" + hashlib.md5(raw.encode("utf-8")).hexdigest()


@router.post("", summary="智能问答")
async def ask_question(req: QARequest, user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    question = (req.question or "").strip()
    if not question:
        return {
            "answer": "请输入想咨询的问题。",
            "related_plans": [],
            "confidence": 0.0,
            "source": "local",
            "provider": "knowledge_base",
        }

    history = _normalize_history(req.history)
    cache_key = _cache_key(question, history)
    cached = await cache.get_json(cache_key)
    if cached is not None:
        return cached

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

    local_result = dict(respond_qa(question, kb_items))
    local_result["source"] = "local"
    local_result["provider"] = "knowledge_base"

    if local_result.get("confidence", 0) >= LOCAL_CONFIDENCE_THRESHOLD:
        await cache.set_json(cache_key, local_result, LOCAL_CACHE_TTL)
        return local_result

    if ai.is_available():
        context = [item["answer"] for item in kb_items if item["answer"]][:5]
        ai_result = await ai.ask_ai(question, context=context, history=history)
        if ai_result:
            result = {
                "answer": ai_result["answer"],
                "related_plans": local_result.get("related_plans", []),
                "confidence": local_result.get("confidence", 0.0),
                "source": "ai",
                "provider": ai_result.get("provider", "huawei"),
            }
            await cache.set_json(cache_key, result, AI_CACHE_TTL)
            return result

    await cache.set_json(cache_key, local_result, LOCAL_CACHE_TTL)
    return local_result