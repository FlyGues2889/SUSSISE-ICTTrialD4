import os
import time

from jose import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "sedentary-health-secret-2026")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 72


def create_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = int(time.time()) + TOKEN_EXPIRE_HOURS * 3600
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def parse_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])