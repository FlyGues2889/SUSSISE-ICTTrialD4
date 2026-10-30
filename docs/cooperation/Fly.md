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
   │   ├─ db/schema.sql       8 张建表 DDL
   │   ├─ db/seed_plans.sql   36 个运动方案种子
   │   ├─ scripts/seed_demo.py 演示账号数据预置（--reset 可复位）
   │   └─ requirements.txt
   └─ frontend/
       ├─ src/views/          Login Home Assessment Plans Tracking TrainingSession Profile Guidelines Qa（9 页）
       ├─ src/components/     ui/ + MovementImage（动作示意图）
       ├─ src/api/            local.js(mock) / remote.js(axios) / index.js(按环境切换)
       ├─ src/mock/           演示数据 + demo.js（一键演示账号）+ healthEvidence.js（WHO/NHS/CSP/CSEP/HHS 指南节选）
       ├─ src/router/ src/styles/
       ├─ .env / .env.cloud   demo(mock) / cloud(真实后端) 双模式
       └─ vite.config.js      /api 代理到 :8001
   ├─ deploy/                 nginx.conf / sedentary-api.service / api.env.example / README.md（部署手册）
   └─ 同仓库 docs/submission/  七项申报交付物（申报书、架构图、视频脚本、在线地址、答辩 PPT、方案库、CodeArts 说明）
```


## 3. 技术栈

| 层 | 选型 |
|---|---|
| 后端 | FastAPI 0.111 + uvicorn + SQLAlchemy 2.0(async) + aiomysql/aiosqlite + redis + python-jose(JWT) + passlib(bcrypt) |
| 前端 | Vue 3.4 + Vite 5 + Pinia + vue-router + axios；图表用纯 SVG/CSS 手绘；包管理 **pnpm** |
| 数据库 | MySQL 8.0（8 张表），本地可用 SQLite 兜底 |
| 缓存 | Redis 可选（热门方案 300s / 问答 3600s / 连续打卡 300s）；未配 `REDIS_URL` 自动降级进程内字典 |
| 部署 | 华为云 ECS + RDS MySQL + Nginx；DCS Redis 为可选优化 |

## 4. 数据模型（8 表）

| 表 | 关键字段 | 说明 |
|---|---|---|
| user | user_id, nickname, phone, password_hash, age, occupation, history | 用户档案 |
| assessment | assessment_id, user_id, area, answers(JSON), risk_level, need_medical | 评估记录 |
| exercise_plan | plan_id, name, duration_min, target_area, scene, movements(JSON) | 方案库（36 条） |
| training_log | log_id, user_id, plan_id, duration_actual, completed, created_at | 训练记录 |
| reminder_setting | user_id, interval_min, active_hours, enabled | 提醒设置 |
| knowledge_base | kb_id, question, answer, keywords, related_plans(JSON) | 知识库 |
| plan_favorite | user_id, plan_id | 收藏关系（官方 + 自定义方案共用） |
| custom_plan | plan_id, user_id, name, target_area, duration_min, scene, movements(JSON) | 用户自建方案（ID 从 900000 起） |

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

环境变量：`DB_HOST/DB_PORT/DB_USER/DB_PASS/DB_NAME/JWT_SECRET`，可选 `REDIS_URL`。Swagger 文档：http://127.0.0.1:8001/docs。完整部署见 `project/deploy/README.md`（资源清单 + 8 项上线验收），本地/云差异见 `project/使用指南.md`。

## 6. 当前状态

架构师已于 2026-10-21 完成走查并修复全部 P0/P1：

| 问题 | 状态 |
|---|---|
| F1 前端纯 mock 无联通 | ✅ 已拆 local/remote 双模式，cloud 模式全链路真实联通 |
| F2 后端注册缺 commit | ✅ 已补，注册可落库 |
| F3 底栏遮挡表单按钮 | ✅ 已加底部安全间距 |
| F4 方案推荐未接评估结果 | ✅ 已去掉硬编码 medium，按最近评估 risk_level 推荐 |

2026-10-30 前端视觉与流程重构（明细见 `docs/AIWorkflow/02_团队分工/工程与部署_工作记录.md`）：
- 全站由玻璃拟态改为平面极简：白卡 + 1px 边框，禁止 `box-shadow` / `backdrop-filter`，令牌集中在 `src/styles/tokens.css`。
- 首页改为单卡「今天建议」（开始 / 换一组），登录仅必填昵称，评估 24 题逐题浮现，评分与红线逻辑未改。
- 新增 `/guidelines` 指南依据页与 `src/mock/healthEvidence.js`（WHO/NHS/CSP/CSEP/HHS 共 9 条节选），首页、评估报告、跟练页同步引用。

2026-10-30 P2/P3 清单（F5–F16）已全部处理：
- 跟练页离开/刷新弹确认并隐藏底栏；评估历史按轮次合并展示。
- 提醒活跃时段改时间选择器；柱状图按最大值归一化；方案页进入即自动推荐并给出空态引导。
- 后端注册/登录改用 bcrypt（`password_hash`），手机号冲突返回 409；401 统一清理凭证并跳登录。
- 新增 `seed_kb.sql`、`mock/kb.js` 与 `/qa` 问答页，问答匹配按关键词长度加权；补充 `favicon.svg`。

2026-10-31 交付收尾（明细见 `docs/AIWorkflow/02_团队分工/工程与部署_工作记录.md`）：
- 演示数据：`backend/scripts/seed_demo.py`（账号 990001 常规 / 990002 高风险，`--reset` 复位）+ 前端 `mock/demo.js`，登录页两个演示按钮。
- 新增 F8 追踪可视化（SVG 改善趋势折线 + 部位关注度）与 F9 方案收藏 / 自定义（新增 `plan_favorite`、`custom_plan` 两表与 5 个接口）。
- 缓存改为可选：`app/services/cache.py` 统一入口，未配 `REDIS_URL` 自动降级进程内字典。
- 修正评估报告与交接文档中「单侧满分 18.3」的错误表述，正确为 **36.6**；`/history` 补返回 `risk_grade`。
- 部署材料：`project/deploy/` 四件套；七项申报交付物落在 `docs/submission/`。
- 前端移除未使用的 `echarts` 依赖，图表全部为纯 SVG/CSS，与 PRD 技术栈表述一致。
- 演示登录打通：新增 `POST /api/auth/demo-login`（`profile=normal|high`），登录页「演示账号」在 Mock 模式载入本地数据、在 cloud 模式换取真实 token。
- 安全加固：`risk_level=high` 时推荐接口返回 `{plans:[], blocked:true}`，首页与方案页均不出现训练入口；风险等级改取「最新一轮最高档」（`src/utils/risk.js`），避免新做的低风险评估覆盖旧的高风险结论。

2026-10-31 增量（首页入口 / 全局提醒 / 问答 AI）：
- 首页「换一组」旁新增「所有方案」入口，高风险时隐藏。
- 提醒改为全局单例 `src/composables/useReminder.js`：`setTimeout` 精确调度替代 30 秒轮询，跨页面保持、`localStorage` 记录上次触发、活跃时段外顺延，支持通知、振动与点击跳转；`Tracking.vue` 只做读写。
- 问答三级降级：本地知识库命中（置信度 ≥ 0.25）→ 华为云 AI（`app/services/ai.py`，`AI_PROVIDER=huawei` 时启用）→ 固定拒答文案；`/api/qa` 返回 `source` / `provider`，支持 `history` 多轮上下文；`Qa.vue` 标注「知识库 / AI 回答」。

## 7. 协作约定

- 沟通用简体中文，代码/命令/变量用英文
- CSS 类名 kebab-case；偏好 Vue Composition API + CSS 变量
- 不引入第三方重型服务，基于华为云技术栈
- 改动后跑 `python -m py_compile`（后端）与 `pnpm build`（前端）验证
- 关键决策与审查记录留在 `docs/AIWorkflow/`，不在代码里堆注释
- 详细规约见根目录 `AGENTS.MD`