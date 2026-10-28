from fastapi import Depends, HTTPException, Header
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import parse_token
from app.db.mysql import get_session


async def get_current_user(authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="认证信息格式错误")
    token = authorization[7:]
    try:
        payload = parse_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="认证已过期，请重新登录")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的认证信息")

    row = await session.execute(text("SELECT user_id, nickname, age, occupation, history FROM user WHERE user_id = :uid"), {"uid": user_id})
    user = row.first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return {
        "user_id": user.user_id,
        "nickname": user.nickname,
        "age": user.age,
        "occupation": user.occupation,
        "history": user.history,
    }