import asyncio
import json
import os
import urllib.request

AI_PROVIDER = os.getenv("AI_PROVIDER", "none").strip().lower()
HUAWEI_AI_ENDPOINT = os.getenv("HUAWEI_AI_ENDPOINT", "").strip()
HUAWEI_AI_TOKEN = os.getenv("HUAWEI_AI_TOKEN", "").strip()
HUAWEI_AI_MODEL = os.getenv("HUAWEI_AI_MODEL", "pangu").strip()
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", "15"))

SYSTEM_PROMPT = """你是久坐人群运动健康助手，只回答与肩颈、腰背、久坐行为、办公场景运动相关的问题。
必须遵守以下规则：
1. 不做疾病诊断，不开药，不解读影像或化验报告；
2. 出现放射性疼痛、肢体麻木无力、夜间痛醒、外伤后疼痛时，直接建议就医；
3. 回答控制在 120 字以内，先给结论，再给 1-2 个可立即执行的动作或建议；
4. 信息不足时说明无法判断，并建议咨询康复科或骨科医生；
5. 不使用夸张承诺，不推荐器械、药物与保健品。"""


def is_available() -> bool:
    return AI_PROVIDER == "huawei" and bool(HUAWEI_AI_ENDPOINT)


def _extract_answer(data: dict) -> str:
    choices = data.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = (message.get("content") or "").strip()
        if content:
            return content
    for key in ("answer", "result", "content", "text"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _post(payload: dict) -> dict:
    request = urllib.request.Request(
        HUAWEI_AI_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {HUAWEI_AI_TOKEN}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=AI_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


async def ask_ai(question: str, context: list[str] | None = None, history: list[dict] | None = None) -> dict | None:
    if not is_available():
        return None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        reference = "\n".join(item for item in context[:5] if item)
        if reference:
            messages.append({
                "role": "system",
                "content": "以下是本地知识库中可能相关的内容，可参考但不要照抄：\n" + reference,
            })
    for item in (history or [])[-4:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": HUAWEI_AI_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 400,
    }

    try:
        data = await asyncio.to_thread(_post, payload)
    except Exception:
        return None

    answer = _extract_answer(data)
    if not answer:
        return None
    return {"answer": answer, "provider": "huawei", "model": HUAWEI_AI_MODEL}