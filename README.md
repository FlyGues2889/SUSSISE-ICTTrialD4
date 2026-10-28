# 久坐肩颈腰背科学运动干预助手

> 华为 ICT 大赛创新赛道 赛题 1 · 参赛单位 SUS SISE
> 体态自评 → AI 匹配碎片化运动方案 → 久坐提醒 → 进度追踪

---
## 成员应关注

1. **先读 `AGENTS.MD`** —— 构建命令（`python -m py_compile` / `pnpm build`）、沟通规约、指令优先级。
2. **再读 `docs/cooperation/Fly.md`** —— 交接文档，含目标、技术栈、数据模型、当前状态速览。
3. **`docs/AIWorkflow/PRD_项目需求文档.md`** —— 任何功能改动先对齐 PRD 的功能清单与验收标准。
4. **`docs/AIWorkflow/架构师审查反馈_20261021.md`** —— P0/P1（联通、注册落库、底栏遮挡、推荐接评估）已修复；**P2/P3 待办**（F5–F16：评估分数展示、跟练退出保护、评估历史重复记录、语义色统一、提醒时段校验、柱状图溢出、时间戳本地化、方案空态引导、401 拦截、login 密码契约、智能问答占位、favicon）是新成员首要接手项。
5. **双模式约定**：默认 `pnpm dev` 走 mock（演示态），`pnpm dev:cloud` 走真实后端；改 API 层时两模式都要兼顾。
6. **合规红线**：健康指导工具，不诊断不治疗；高风险强制就医提示，不推荐方案——评估与推荐逻辑改动必须守住这条。


## 项目结构

```
D4/
├─ AGENTS.MD                  项目规约（构建/测试命令、协作约定，最高优先级）
├─ README.md                  本文件
├─ skills/                    4 个 CodeArts 自定义 Skill（Python）
│   ├─ posture_assessment.py  体态评估评分（肩颈/腰背各 8 题 + 安全红线）
│   ├─ plan_matcher.py        方案匹配推荐（加权排序取前 3）
│   ├─ safety_check.py        安全边界/就医红线判定
│   ├─ qa_responder.py        智能问答（关键词匹配知识库）
│   └─ generate_plans.py      生成 36 个方案种子 SQL
├─ docs/
│   ├─ AIWorkflow/            AI 调研与工作流文档（见第 2 节）
│   └─ cooperation/Fly.md     成员交接文档
└─ project/
   ├─ start.bat               一键启动
   ├─ 使用指南.md             本地/云部署完整指南
   ├─ backend/                FastAPI 后端
   │   ├─ app/main.py         入口，路由注册
   │   ├─ app/core/           security.py(JWT) + deps.py(认证依赖)
   │   ├─ app/db/             SQLAlchemy async 连接
   │   ├─ app/routers/        auth assessment plan training reminder qa
   │   ├─ db/schema.sql       6 张建表 DDL
   │   ├─ db/seed_plans.sql   36 个运动方案种子
   │   └─ requirements.txt
   └─ frontend/               Vue3 前端
       ├─ src/views/          Login Home Assessment Plans Tracking TrainingSession Profile
       ├─ src/components/     ui/ + MovementImage（动作示意图）
       ├─ src/api/            local.js(mock) / remote.js(axios) / index.js(按环境切换)
       ├─ src/router/ src/mock/ src/styles/
       ├─ .env / .env.cloud   demo(mock) / cloud(真实后端) 双模式
       └─ vite.config.js      /api 代理到 :8001
```

**技术栈**：后端 FastAPI + SQLAlchemy(async) + MySQL/SQLite + Redis + JWT；前端 Vue3 + Vite + Pinia + ECharts，包管理 pnpm。

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

环境要求：Python ≥ 3.11、Node ≥ 18、pnpm ≥ 8、MySQL 8.0、Redis ≥ 6。

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

数据库初始化（首次）：创建库后依次导入 `db/schema.sql` 与 `db/seed_plans.sql`（36 个方案）。环境变量：`DB_HOST/DB_PORT/DB_USER/DB_PASS/DB_NAME/JWT_SECRET`。Swagger 文档：http://127.0.0.1:8001/docs。

华为云部署（ECS + RDS + DCS + Nginx）详见 `project/使用指南.md` 第 8 节。