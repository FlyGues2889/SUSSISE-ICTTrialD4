import os
import sys

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token
from app.db.mysql import get_session

router = APIRouter()


class RegisterRequest(BaseModel):
    nickname: str = "匿名用户"
    phone: str | None = None
    password: str | None = None
    age: int | None = None
    occupation: str | None = None
    history: str | None = None


class LoginRequest(BaseModel):
    phone: str
    password: str


@router.post("/register", summary="用户注册")
async def register(req: RegisterRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        text(
            "INSERT INTO user (nickname, phone, age, occupation, history) "
            "VALUES (:nickname, :phone, :age, :occupation, :history)"
        ),
        {
            "nickname": req.nickname,
            "phone": req.phone,
            "age": req.age,
            "occupation": req.occupation,
            "history": req.history,
        },
    )
    user_id = result.lastrowid
    await session.commit()
    token = create_token({"user_id": user_id, "nickname": req.nickname})
    return {"token": token, "user_id": user_id, "nickname": req.nickname}


@router.post("/login", summary="用户登录")
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    row = await session.execute(
        text("SELECT user_id, nickname FROM user WHERE phone = :phone AND password_hash = :password"),
        {"phone": req.phone, "password": req.password},
    )
    user = row.first()
    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    token = create_token({"user_id": user.user_id, "nickname": user.nickname})
    return {"token": token, "user_id": user.user_id, "nickname": user.nickname}