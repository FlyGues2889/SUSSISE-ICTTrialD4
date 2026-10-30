# 久坐肩颈腰背科学运动干预助手

> 华为 ICT 大赛创新赛道 赛题 1 · 参赛单位 SUS SISE
> 体态自评 → AI 匹配碎片化运动方案 → 久坐提醒 → 进度追踪

---
## 成员应关注

1. **先读 `AGENTS.MD`** —— 构建命令（`python -m py_compile` / `pnpm build`）、沟通规约、指令优先级。
2. **再读 `docs/cooperation/Fly.md`** —— 交接文档，含目标、技术栈、数据模型、当前状态速览。
3. **`docs/AIWorkflow/PRD_项目需求文档.md`** —— 任何功能改动先对齐 PRD 的功能清单与验收标准。
4. **`docs/AIWorkflow/架构师审查反馈_20261021.md`** —— P0/P1 与 P2/P3（F5–F16）已全部关闭；后续改动请新增条目而非回填旧结论。
5. **双模式约定**：默认 `pnpm dev` 走 mock（演示态），`pnpm dev:cloud` 走真实后端；改 API 层时两模式都要兼顾。**上云必须用 `pnpm build:cloud`**，`pnpm build` 的产物走 Mock 数据。
6. **合规红线**：健康指导工具，不诊断不治疗；高风险强制就医提示，不推荐方案——评估与推荐逻辑改动必须守住这条。
7. **演示与申报**：一键演示数据见 `project/backend/scripts/seed_demo.py`（`--reset` 复位）；七项申报交付物在 `docs/submission/`；部署手册在 `project/deploy/README.md`。


## 项目结构

```
D4/
├─ AGENTS.MD                  项目规约（构建/测试命令、协作约定，最高优先级）
├─ README.md                  本文件
├─ skills/                    4 个 CodeArts 自定义 Skill（Python）
│   ├─ posture_assessment.py  体态评估评分（肩颈/腰背各 12 题 + 安全红线）
│   ├─ plan_matcher.py        方案匹配推荐（加权排序取前 3）
│   ├─ safety_check.py        安全边界/就医红线判定
│   ├─ qa_responder.py        智能问答（关键词匹配知识库）
│   └─ generate_plans.py      生成 36 个方案种子 SQL
├─ docs/
│   ├─ AIWorkflow/            AI 调研与工作流文档（见第 2 节）
│   ├─ cooperation/Fly.md     成员交接文档
│   └─ submission/            七项申报交付物（申报书/架构图/视频脚本/在线地址/答辩 PPT/方案库/CodeArts 说明）
└─ project/
   ├─ start.bat               一键启动
   ├─ 使用指南.md             本地/云部署完整指南
   ├─ deploy/                 部署四件套（nginx.conf / systemd / env 模板 / README）
   ├─ backend/                FastAPI 后端
   │   ├─ app/main.py         入口，路由注册
   │   ├─ app/core/           security.py(JWT) + deps.py(认证依赖)
   │   ├─ app/db/             SQLAlchemy async 连接（启动自动补种知识库）
   │   ├─ app/routers/        auth assessment plan training reminder qa
   │   ├─ app/services/       cache.py（Redis 可选，未配置降级进程内字典）
   │   ├─ scripts/seed_demo.py 演示账号数据预置（--reset 复位）
   │   ├─ db/schema.sql       8 张建表 DDL
   │   ├─ db/seed_plans.sql   36 个运动方案种子
   │   ├─ db/seed_kb.sql      10 条智能问答知识库
   │   └─ requirements.txt
   └─ frontend/               Vue3 前端
       ├─ src/views/          Login Home Assessment Plans Tracking TrainingSession Profile Guidelines Qa
       ├─ src/components/     ui/ + MovementImage（动作示意图）
       ├─ src/api/            local.js(mock) / remote.js(axios) / index.js(按环境切换)
       ├─ src/mock/           演示数据 + demo.js（一键演示账号）+ healthEvidence.js（权威健康指南库）
       ├─ src/router/ src/styles/
       ├─ .env / .env.cloud   demo(mock) / cloud(真实后端) 双模式
       └─ vite.config.js      /api 代理到 :8001
```

**技术栈**：后端 FastAPI + SQLAlchemy(async) + MySQL/SQLite + Redis（可选）+ JWT；前端 Vue3 + Vite + Pinia + 自研 UI 组件，图表用纯 SVG/CSS 手绘，包管理 pnpm。

**评估规则**：肩颈/腰背各 12 题、6 维度、加权总分（满分 36.6），四档评级（低/中低/中高/高，中低与中高以 18.3 分为界，底层 `risk_level` 仍为低/中/高三档）。红线题（N5/N11/B5/B11）得分 ≥ 2 或总分 ≥ 23.79 强制就医提示。

## AI 提示词与过程文档

所有 AI 调研、分工、审查产物在 `docs/AIWorkflow/`，是本项目需求与决策的来源：

| 文档 | 用途 |
|---|---|
| `PRD_项目需求文档.md` | 产品需求文档，功能清单/数据模型/验收标准/排期的权威来源 |
| `01_调研/调研报告_*.md` | 久坐健康市场调研，论证三重空白与专业壁垒 |
| `01_调研/初赛落地全方案_*.md` | 初赛 8 周落地方案，含排期与亮点包装 |
| `02_团队分工/*_PRD.md` | 三角色（算法/产品/工程）分工 PRD |
| `02_团队分工/*_工作记录.md` | 各角色工作记录 |
| `架构师审查反馈_20261021.md` | 架构师走查结论、问题清单（P0–P3）、修复进展 |

`AGENTS.MD` 是 AI 协作规约入口（构建/测试命令、沟通与执行约定），项目范围内优先级最高。`skills/` 下 4 个 Skill 即赛题要求的 CodeArts 自定义 Skills，后端通过 `sys.path` 自动加载。

## 启动方式

环境要求：Python ≥ 3.11、Node ≥ 18、pnpm ≥ 8、MySQL 8.0。Redis ≥ 6 可选，不配 `REDIS_URL` 时自动降级为进程内缓存。

```bash
# 后端（端口 8001）
cd project/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 前端（端口 5174，默认 mock 模式）
cd project/frontend
pnpm install && pnpm dev

# 真实联调模式
pnpm dev:cloud        # 使用 .env.cloud，请求走真实后端
pnpm build:cloud      # 生产构建联调版
```

数据库初始化（首次）：创建库后依次导入 `db/schema.sql`（8 张表）、`db/seed_plans.sql`（36 个方案）与 `db/seed_kb.sql`（10 条问答，启动时也会自动补种）。环境变量：`DB_HOST/DB_PORT/DB_USER/DB_PASS/DB_NAME/JWT_SECRET`，可选 `REDIS_URL`。Swagger 文档：http://127.0.0.1:8001/docs。

演示数据：`python project/backend/scripts/seed_demo.py --reset` 生成账号 `990001`（常规，5 轮评估 + 7 条训练 + 2 条收藏）与 `990002`（高风险，红线命中）。登录页直接点「演示账号」/「高风险演示」即可，云端调用 `POST /api/auth/demo-login`，Mock 模式载入本地数据。

华为云部署详见 `project/deploy/README.md`（资源清单、7 步部署、8 项上线验收）；本地/云差异与常见问题见 `project/使用指南.md` 第 8 节。