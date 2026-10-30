-- 久坐肩颈腰背科学运动干预助手 数据库 Schema
-- RDS MySQL 8.0

CREATE TABLE IF NOT EXISTS user (
    user_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
    nickname     VARCHAR(50),
    phone        VARCHAR(20) UNIQUE,
    password_hash VARCHAR(128),
    age          INT,
    occupation   VARCHAR(50),
    history      TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assessment (
    assessment_id  BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id        BIGINT NOT NULL,
    area           VARCHAR(20) NOT NULL,
    answers        JSON NOT NULL,
    total_score    INT NOT NULL,
    risk_level     VARCHAR(10) NOT NULL,
    problem_points JSON,
    suggestion     TEXT,
    need_medical   BOOLEAN DEFAULT FALSE,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_user_date (user_id, created_at)
);

CREATE TABLE IF NOT EXISTS exercise_plan (
    plan_id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    duration_min    INT NOT NULL,
    target_area     VARCHAR(20) NOT NULL,
    scene           VARCHAR(20) NOT NULL,
    movements       JSON NOT NULL,
    suitable_level  VARCHAR(50),
    contraindication TEXT,
    description     TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_area_duration_scene (target_area, duration_min, scene)
);

CREATE TABLE IF NOT EXISTS training_log (
    log_id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT NOT NULL,
    plan_id         BIGINT NOT NULL,
    duration_actual INT,
    completed       BOOLEAN DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_date (user_id, created_at)
);

CREATE TABLE IF NOT EXISTS reminder_setting (
    reminder_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id        BIGINT NOT NULL UNIQUE,
    interval_min   INT DEFAULT 45,
    active_hours   VARCHAR(50) DEFAULT '09:00-18:00',
    enabled        BOOLEAN DEFAULT TRUE,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    kb_id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    question       VARCHAR(200) NOT NULL,
    answer         TEXT NOT NULL,
    keywords       VARCHAR(200),
    related_plans  JSON,
    category       VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS plan_favorite (
    user_id    BIGINT NOT NULL,
    plan_id    BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, plan_id)
);

CREATE TABLE IF NOT EXISTS custom_plan (
    plan_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id      BIGINT NOT NULL,
    name         VARCHAR(100) NOT NULL,
    duration_min INT NOT NULL,
    target_area  VARCHAR(20) NOT NULL,
    scene        VARCHAR(20) NOT NULL,
    movements    JSON NOT NULL,
    description  TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_custom_user (user_id)
);