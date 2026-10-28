-- SQLite 兼容版 Schema（本地开发用，无需安装 MySQL）

CREATE TABLE IF NOT EXISTS user (
    user_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname     TEXT,
    phone        TEXT UNIQUE,
    password_hash TEXT,
    age          INTEGER,
    occupation   TEXT,
    history      TEXT,
    created_at   TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS assessment (
    assessment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    area           TEXT NOT NULL,
    answers        TEXT NOT NULL,
    total_score    INTEGER NOT NULL,
    risk_level     TEXT NOT NULL,
    problem_points TEXT,
    suggestion     TEXT,
    need_medical   INTEGER DEFAULT 0,
    created_at     TEXT DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_assessment_user ON assessment(user_id);
CREATE INDEX IF NOT EXISTS idx_assessment_user_date ON assessment(user_id, created_at);

CREATE TABLE IF NOT EXISTS exercise_plan (
    plan_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    duration_min    INTEGER NOT NULL,
    target_area     TEXT NOT NULL,
    scene           TEXT NOT NULL,
    movements       TEXT NOT NULL,
    suitable_level  TEXT,
    contraindication TEXT,
    description     TEXT,
    created_at      TEXT DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_plan_ads ON exercise_plan(target_area, duration_min, scene);

CREATE TABLE IF NOT EXISTS training_log (
    log_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    plan_id         INTEGER NOT NULL,
    duration_actual INTEGER,
    completed       INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_training_user_date ON training_log(user_id, created_at);

CREATE TABLE IF NOT EXISTS reminder_setting (
    reminder_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL UNIQUE,
    interval_min   INTEGER DEFAULT 45,
    active_hours   TEXT DEFAULT '09:00-18:00',
    enabled        INTEGER DEFAULT 1,
    updated_at     TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    kb_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question       TEXT NOT NULL,
    answer         TEXT NOT NULL,
    keywords       TEXT,
    related_plans  TEXT,
    category       TEXT
);