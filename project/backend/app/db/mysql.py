import json
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "sedentary_health")

USE_SQLITE = not DB_HOST or not os.getenv("DB_FORCE_MYSQL")

if USE_SQLITE:
    DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "db")
    DB_PATH = os.path.join(DB_DIR, "sedentary_health.db")
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
else:
    DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db():
    if USE_SQLITE:
        schema_path = os.path.join(os.path.dirname(__file__), "..", "..", "db", "schema_sqlite.sql")
    else:
        schema_path = os.path.join(os.path.dirname(__file__), "..", "..", "db", "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    async with engine.begin() as conn:
        for stmt in schema_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                await conn.execute(text(stmt))

    await _seed_plans()


async def _seed_plans():
    skills_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "skills")
    if skills_path not in sys.path:
        sys.path.insert(0, skills_path)
    from generate_plans import generate_plans

    plans = generate_plans()
    async with async_session() as session:
        count = await session.execute(text("SELECT COUNT(*) FROM exercise_plan"))
        if count.scalar() > 0:
            return
        for p in plans:
            await session.execute(
                text(
                    "INSERT INTO exercise_plan (name, duration_min, target_area, scene, movements, suitable_level, contraindication, description) "
                    "VALUES (:name, :dur, :area, :scene, :mov, :suit, :contra, :desc)"
                ),
                {
                    "name": p["name"],
                    "dur": p["duration_min"],
                    "area": p["target_area"],
                    "scene": p["scene"],
                    "mov": json.dumps(p["movements"], ensure_ascii=False),
                    "suit": p["suitable_level"],
                    "contra": p["contraindication"],
                    "desc": p["description"],
                },
            )
        await session.commit()