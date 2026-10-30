"""载入演示数据：一个中低风险主账号 + 一个高风险备用账号。

用法（项目根目录或任意位置）：
    python project/backend/scripts/seed_demo.py
    python project/backend/scripts/seed_demo.py --reset   # 先清空两个演示账号的旧数据

数据会先经 skills/posture_assessment.py 真实评分，再写入 assessment 表，
因此演示账号的分数、问题点、建议与线上算法完全一致。
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "..", "..", "skills"))
for p in (BACKEND_DIR, SKILLS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from sqlalchemy import text

from app.db.mysql import async_session, init_db
from posture_assessment import assess_posture
from safety_check import check_safety

NECK_IDS = ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10", "N11", "N12"]
BACK_IDS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12"]

MAIN_USER = {"user_id": 990001, "nickname": "演示·小林", "age": 29, "occupation": "程序员"}
HIGH_USER = {"user_id": 990002, "nickname": "演示·高风险", "age": 42, "occupation": "财务/行政"}

MAIN_ROUNDS = [
    (28, {"N1": 3, "N2": 2, "N3": 3, "N4": 2, "N6": 2, "N7": 2, "N8": 2, "N9": 3, "N10": 2, "N12": 2},
         {"B1": 3, "B3": 3, "B4": 2, "B6": 2, "B9": 2, "B10": 1}),
    (21, {"N1": 2, "N2": 2, "N3": 3, "N4": 2, "N6": 1, "N7": 2, "N8": 3, "N9": 2, "N10": 1, "N12": 1},
         {"B1": 2, "B3": 2, "B4": 2, "B6": 1, "B10": 1, "B12": 2}),
    (14, {"N1": 3, "N2": 1, "N3": 3, "N4": 2, "N6": 1, "N7": 2, "N9": 2, "N10": 1, "N12": 2},
         {"B1": 2, "B3": 2, "B4": 1, "B7": 1, "B10": 1, "B12": 1}),
    (7, {"N1": 3, "N3": 2, "N4": 2, "N6": 1, "N7": 2, "N9": 2, "N10": 1, "N12": 2},
        {"B1": 2, "B3": 1, "B4": 1, "B10": 1}),
    (0, {"N1": 3, "N3": 2, "N4": 2, "N6": 1, "N7": 2, "N9": 2, "N12": 2},
        {"B1": 1, "B3": 1, "B4": 1, "B10": 1}),
]

HIGH_ROUNDS = [
    (0, {"N1": 3, "N2": 3, "N3": 3, "N4": 3, "N5": 3, "N6": 3, "N7": 3, "N8": 3, "N9": 3, "N10": 3, "N11": 3, "N12": 3},
        {"B1": 3, "B3": 3, "B4": 3, "B5": 3, "B6": 3, "B10": 3, "B11": 3}),
]

MAIN_TRAININGS = [(0, 3), (1, 3), (2, 5), (3, 3), (4, 5), (6, 3), (8, 5)]


def fill(ids, sparse):
    return {qid: sparse.get(qid, 0) for qid in ids}


def stamp(days_ago, hour, minute, second=0):
    d = datetime.now() - timedelta(days=days_ago)
    return d.replace(hour=hour, minute=minute, second=second, microsecond=0)


async def clear_demo(session):
    for uid in (MAIN_USER["user_id"], HIGH_USER["user_id"]):
        await session.execute(text("DELETE FROM plan_favorite WHERE user_id = :uid"), {"uid": uid})
        await session.execute(text("DELETE FROM custom_plan WHERE user_id = :uid"), {"uid": uid})
        await session.execute(text("DELETE FROM assessment WHERE user_id = :uid"), {"uid": uid})
        await session.execute(text("DELETE FROM training_log WHERE user_id = :uid"), {"uid": uid})
        await session.execute(text("DELETE FROM reminder_setting WHERE user_id = :uid"), {"uid": uid})
        await session.execute(text("DELETE FROM user WHERE user_id = :uid"), {"uid": uid})


async def insert_user(session, user):
    await session.execute(
        text(
            "INSERT INTO user (user_id, nickname, age, occupation, created_at) "
            "VALUES (:uid, :nick, :age, :occ, :created)"
        ),
        {
            "uid": user["user_id"],
            "nick": user["nickname"],
            "age": user["age"],
            "occ": user["occupation"],
            "created": stamp(40, 9, 0).strftime("%Y-%m-%d %H:%M:%S"),
        },
    )


async def insert_round(session, user, rounds):
    for days_ago, neck, back in rounds:
        for offset, area, sparse, ids in ((0, "neck", neck, NECK_IDS), (1, "back", back, BACK_IDS)):
            answers = fill(ids, sparse)
            result = assess_posture(area, answers)
            safety = check_safety(result["risk_level"], result["red_line_hit"], user["age"], None)
            created = stamp(days_ago, 10, 20, offset * 5)
            await session.execute(
                text(
                    "INSERT INTO assessment (user_id, area, answers, total_score, risk_level, problem_points, suggestion, need_medical, created_at) "
                    "VALUES (:uid, :area, :answers, :score, :risk, :points, :sugg, :medical, :created)"
                ),
                {
                    "uid": user["user_id"],
                    "area": area,
                    "answers": json.dumps(answers, ensure_ascii=False),
                    "score": result["total_score"],
                    "risk": result["risk_level"],
                    "points": json.dumps(result["problem_points"], ensure_ascii=False),
                    "sugg": result["suggestion"],
                    "medical": 1 if safety["need_medical"] else 0,
                    "created": created.strftime("%Y-%m-%d %H:%M:%S"),
                },
            )


async def plan_id_for(session, area, duration, scene):
    row = await session.execute(
        text(
            "SELECT plan_id FROM exercise_plan WHERE target_area = :area AND duration_min = :dur AND scene = :scene "
            "ORDER BY plan_id LIMIT 1"
        ),
        {"area": area, "dur": duration, "scene": scene},
    )
    value = row.scalar()
    return value


async def insert_training(session, user, plan_ids):
    for i, (days_ago, duration) in enumerate(MAIN_TRAININGS):
        pid = plan_ids[duration]
        if not pid:
            continue
        await session.execute(
            text(
                "INSERT INTO training_log (user_id, plan_id, duration_actual, completed, created_at) "
                "VALUES (:uid, :pid, :dur, 1, :created)"
            ),
            {
                "uid": user["user_id"],
                "pid": pid,
                "dur": duration,
                "created": stamp(days_ago, 15, 30, i % 50).strftime("%Y-%m-%d %H:%M:%S"),
            },
        )


async def insert_favorites(session, user, plan_ids):
    for i, pid in enumerate(dict.fromkeys(plan_ids)):
        if not pid:
            continue
        await session.execute(
            text(
                "INSERT INTO plan_favorite (user_id, plan_id, created_at) "
                "VALUES (:uid, :pid, :created)"
            ),
            {
                "uid": user["user_id"],
                "pid": pid,
                "created": stamp(2, 20, 10, i).strftime("%Y-%m-%d %H:%M:%S"),
            },
        )


async def insert_reminder(session, user):
    await session.execute(
        text(
            "INSERT INTO reminder_setting (user_id, interval_min, active_hours, enabled, updated_at) "
            "VALUES (:uid, 45, '09:00-18:00', 1, :updated)"
        ),
        {"uid": user["user_id"], "updated": stamp(0, 9, 30).strftime("%Y-%m-%d %H:%M:%S")},
    )


async def main(reset):
    await init_db()

    async with async_session() as session:
        if reset:
            await clear_demo(session)

        for user in (MAIN_USER, HIGH_USER):
            exists = await session.execute(
                text("SELECT COUNT(*) FROM user WHERE user_id = :uid"), {"uid": user["user_id"]}
            )
            if exists.scalar():
                print(f"[跳过] 演示账号已存在：{user['nickname']}（用 --reset 可重建）")
                continue

            await insert_user(session, user)
            await insert_round(session, user, HIGH_ROUNDS if user is HIGH_USER else MAIN_ROUNDS)
            if user is MAIN_USER:
                plan_ids = {
                    3: await plan_id_for(session, "neck", 3, "desk"),
                    5: await plan_id_for(session, "neck", 5, "desk"),
                }
                await insert_training(session, user, plan_ids)
                await insert_favorites(session, user, [plan_ids[3], plan_ids[5]])
            await insert_reminder(session, user)
            print(f"[完成] {user['nickname']} (user_id={user['user_id']})")

        await session.commit()

    print("\n演示账号：")
    print("  主账号  演示·小林    肩颈 21→18→16→14→13 分，腰背 12→9→7→5→4 分，连续打卡 5 天")
    print("  备用账号 演示·高风险  红线命中（颈部放射痛），用于演示就医提示与方案拦截")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="载入演示数据")
    parser.add_argument("--reset", action="store_true", help="先清除两个演示账号的旧数据再写入")
    args = parser.parse_args()
    asyncio.run(main(args.reset))