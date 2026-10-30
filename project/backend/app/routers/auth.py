from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token
from app.db.mysql import get_session

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BCRYPT_MAX_BYTES = 72


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


class DemoLoginRequest(BaseModel):
    profile: str = "normal"


DEMO_USERS = {"normal": 990001, "high": 990002}


def _hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise HTTPException(status_code=400, detail="密码过长，请控制在 72 字节以内")
    return pwd_context.hash(password)


@router.post("/register", summary="用户注册")
async def register(req: RegisterRequest, session: AsyncSession = Depends(get_session)):
    password_hash = _hash_password(req.password) if req.password else None
    try:
        result = await session.execute(
            text(
                "INSERT INTO user (nickname, phone, password_hash, age, occupation, history) "
                "VALUES (:nickname, :phone, :password_hash, :age, :occupation, :history)"
            ),
            {
                "nickname": req.nickname,
                "phone": req.phone,
                "password_hash": password_hash,
                "age": req.age,
                "occupation": req.occupation,
                "history": req.history,
            },
        )
        user_id = result.lastrowid
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="该手机号已注册")
    token = create_token({"user_id": user_id, "nickname": req.nickname})
    return {"token": token, "user_id": user_id, "nickname": req.nickname}


@router.post("/login", summary="用户登录")
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    row = await session.execute(
        text("SELECT user_id, nickname, password_hash FROM user WHERE phone = :phone"),
        {"phone": req.phone},
    )
    user = row.first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    try:
        valid = pwd_context.verify(req.password, user.password_hash)
    except ValueError:
        valid = False
    if not valid:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    token = create_token({"user_id": user.user_id, "nickname": user.nickname})
    return {"token": token, "user_id": user.user_id, "nickname": user.nickname}

@router.post("/demo-login", summary="演示账号登录")
async def demo_login(req: DemoLoginRequest, session: AsyncSession = Depends(get_session)):
    user_id = DEMO_USERS.get(req.profile)
    if not user_id:
        raise HTTPException(status_code=400, detail="未知的演示类型")
    row = await session.execute(
        text("SELECT user_id, nickname, age, occupation FROM user WHERE user_id = :uid"),
        {"uid": user_id},
    )
    user = row.first()
    if not user:
        raise HTTPException(status_code=404, detail="演示账号未初始化，请先执行 seed_demo.py")
    token = create_token({"user_id": user.user_id, "nickname": user.nickname})
    return {
        "token": token,
        "user_id": user.user_id,
        "nickname": user.nickname,
        "age": user.age,
        "occupation": user.occupation,
    }