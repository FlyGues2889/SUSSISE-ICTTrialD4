# Fly - 交接文档


## 1. 这个项目

久坐肩颈腰背科学运动干预助手面向久坐人群的**轻量化健康运动指导 Web 工具**：体态自评 → AI 匹配碎片化运动方案 → 久坐提醒 → 进度追踪，零门槛即用。

- 目标赛题：华为 ICT 大赛创新赛道 赛题 1
- 周期：8 周初赛
- 工作流程：注册 → 体态评估 → 方案推荐 → 执行方案 → 进度追踪。
- 要求：基于华为云 **CodeArts 智能体 + 自定义 Skills**，使用 **RDS** 持久化、**Redis** 缓存，部署华为云。评审权重：创新性 60% + 应用价值 40%。

- **（重要）合规边界**：健康指导工具，**不诊断不治疗**；高风险强制就医提示，不推荐方案。

## 2. 目录分布

我们只需要重点关注的文字区域：
```
docs/
├─ AIWorkflow/                让AI负责的调研记录区域（PRD需求文档、调研报告、落地全方案、架构师审查反馈、团队分工）
└─ cooperation/               成员间交流的说明文件
```

*注意：大部分MD文档都是给AI阅读和限制的提示词。*

下面是完整项目目录及其说明：

```
D4/
├─ AGENTS.MD                  项目规约（Python+Vue，构建/测试命令）
├─ skills/                    4 个 CodeArts 自定义 Skill（Python）
│   ├─ posture_assessment.py  体态评估评分
│   ├─ plan_matcher.py        方案匹配推荐
│   ├─ safety_check.py        安全边界/就医红线
│   ├─ qa_responder.py        智能问答
│   └─ generate_plans.py      生成 36 个方案种子 SQL
├─ docs/
│   ├─ AIWorkflow/            PRD、调研报告、落地全方案、架构师审查反馈、团队分工
│   └─ cooperation/Lvi.md     本文件
└─ project/
   ├─ start.bat               一键启动
   ├─ 使用指南.md             本地/云部署完整指南（首选入口）
   ├─ backend/
   │   ├─ app/main.py         入口，路由注册
   │   ├─ app/core/           security.py(JWT) + deps.py(认证依赖)
   │   ├─ app/db/             SQLAlchemy async 连接
   │   ├─ app/routers/        auth assessment plan training reminder qa（6 模块）
   │   ├─ db/schema.sql       6 张建表 DDL
   │   ├─ db/seed_plans.sql   36 个运动方案种子
   │   └─ requirements.txt
   └─ frontend/
       ├─ src/views/          Login Home Assessment Plans Tracking TrainingSession Profile（7 页）
       ├─ src/components/     ui/ + MovementImage（动作示意图）
       ├─ src/api/            local.js(mock) / remote.js(axios) / index.js(按环境切换)
       ├─ src/router/ src/mock/ src/styles/
       ├─ .env / .env.cloud   demo(mock) / cloud(真实后端) 双模式
       └─ vite.config.js      /api 代理到 :8001
```


## 3. 技术栈

| 层 | 选型 |
|---|---|
| 后端 | FastAPI 0.111 + uvicorn + SQLAlchemy 2.0(async) + aiomysql/aiosqlite + redis + python-jose(JWT) + passlib(bcrypt) |
| 前端 | Vue 3.4 + Vite 5 + Pinia + vue-router + ECharts + axios；包管理 **pnpm** |
| 数据库 | MySQL 8.0（6 张表），本地可用 SQLite 兜底 |
| 缓存 | Redis（热门方案/会话/打卡/问答） |
| 部署 | 华为云 ECS + RDS MySQL + DCS Redis + Nginx |

## 4. 数据模型（6 表）

| 表 | 关键字段 | 说明 |
|---|---|---|
| user | user_id, nickname, phone, password_hash, age, occupation, history | 用户档案 |
| assessment | assessment_id, user_id, area, answers(JSON), risk_level, need_medical | 评估记录 |
| exercise_plan | plan_id, name, duration_min, target_area, scene, movements(JSON) | 方案库（36 条） |
| training_log | log_id, user_id, plan_id, duration_actual, completed, created_at | 训练记录 |
| reminder_setting | user_id, interval_min, active_hours, enabled | 提醒设置 |
| knowledge_base | kb_id, question, answer, keywords, related_plans(JSON) | 知识库 |

## 5. 启动方式

```bash
# 后端（端口 8001）
cd project/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 前端（端口 5174，默认 mock 模式）
cd project/frontend
pnpm install && pnpm dev

# 真实联调模式
pnpm dev:cloud      # 使用 .env.cloud，请求走真实后端
pnpm build:cloud    # 生产构建联调版
```

环境变量：`DB_HOST/DB_PORT/DB_USER/DB_PASS/DB_NAME/JWT_SECRET`。Swagger 文档：http://127.0.0.1:8001/docs。完整部署见 `project/使用指南.md`。

## 6. 当前状态

架构师已于 2026-10-21 完成走查并修复全部 P0/P1：

| 问题 | 状态 |
|---|---|
| F1 前端纯 mock 无联通 | ✅ 已拆 local/remote 双模式，cloud 模式全链路真实联通 |
| F2 后端注册缺 commit | ✅ 已补，注册可落库 |
| F3 底栏遮挡表单按钮 | ✅ 已加底部安全间距 |
| F4 方案推荐未接评估结果 | ✅ 已去掉硬编码 medium，按最近评估 risk_level 推荐 |

**待办**（P2/P3，见 `docs/AIWorkflow/架构师审查反馈_20261021.md`）：
- F5 评估报告分数展示易误解；F6 跟练页缺退出保护；F7 评估历史重复记录；F8 语义色不统一；F9 提醒时段无校验；F10 柱状图溢出；F11 时间戳未本地化；F12 方案空态无引导
- F13 无 401 全局拦截；F14 login 明文比较密码；F15 智能问答为占位；F16 favicon 404

## 7. 协作约定

- 沟通用简体中文，代码/命令/变量用英文
- CSS 类名 kebab-case；偏好 Vue Composition API + CSS 变量
- 不引入第三方重型服务，基于华为云技术栈
- 改动后跑 `python -m py_compile`（后端）与 `pnpm build`（前端）验证
- 关键决策与审查记录留在 `docs/AIWorkflow/`，不在代码里堆注释
- 详细规约见根目录 `AGENTS.MD`