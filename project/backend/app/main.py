from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mysql import init_db
from app.routers import auth, assessment, plan, training, reminder, qa

app = FastAPI(title="久坐肩颈腰背科学运动干预助手", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(assessment.router, prefix="/api/assessment", tags=["评估"])
app.include_router(plan.router, prefix="/api/plans", tags=["方案"])
app.include_router(training.router, prefix="/api/training", tags=["训练"])
app.include_router(reminder.router, prefix="/api/reminder", tags=["提醒"])
app.include_router(qa.router, prefix="/api/qa", tags=["问答"])


@app.on_event("startup")
async def startup():
    try:
        await init_db()
        print("[启动] 数据库初始化完成")
    except Exception as e:
        print(f"[启动] 数据库初始化失败: {e}")


@app.get("/api/health")
async def health():
    return {"status": "ok"}