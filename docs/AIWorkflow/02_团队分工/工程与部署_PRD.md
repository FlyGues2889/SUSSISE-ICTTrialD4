# 产品功能开发角色需求文档（PRD）

> 版本：v1.0　|　日期：2026-10-21　|　角色：产品功能开发 / 工程与部署（1 人）
> 项目：久坐肩颈腰背科学运动干预助手
> 参赛单位：SUS SISE　|　华为 ICT 大赛 创新赛道 赛题 1
> 上游文档：`D4/PRD_项目需求文档.md`（本文与之保持一致，不得冲突）
> 周期：2 个月初赛周期（8 周）

---

## 1. 角色定位与职责边界

### 1.1 角色定位
负责项目全部前后端代码开发、数据库设计、Redis 缓存实现与 CodeArts Skills 代码落地，将专业内容角色产出的规则与方案转化为**可运行的 Web 应用**。

### 1.2 职责边界

| 维度 | 本角色负责 | 本角色不负责 |
|---|---|---|
| 评估逻辑 | 接口对接、评分计算、结果落库 | 问卷条目设计、评分规则定义（专业内容角色） |
| 方案推荐 | 接口对接、方案查询、匹配排序 | 方案专业内容编写（专业内容角色） |
| 安全边界 | 就医提示接口、方案过滤实现 | 安全规则定义（专业内容角色） |
| 前端 | 全部页面开发、接口联调、移动端适配 | 原型设计、Demo 脚本（产品角色） |
| 后端 | 全部 API 开发、数据层落地、JWT 鉴权 | 业务规则定义 |
| Skills 代码 | 4 个 Skill 的 Python 代码实现 | Skill 业务规则定义（专业内容角色） |
| 部署 | ECS 部署、环境配置、Docker 打包 | 华为云资源采购审批 |

### 1.3 核心交付物
1. 前端 Web 应用（Vue3 + Element Plus，移动端优先）
2. 后端 API 服务（FastAPI + SQLAlchemy）
3. 4 个 CodeArts Skills Python 模块
4. 数据库建表 SQL（RDS MySQL）
5. Redis 缓存实现
6. 接口文档
7. 部署脚本（Dockerfile + docker-compose）

---

## 2. 负责的技术需求

### 2.1 前端技术需求

| 需求项 | 说明 | 优先级 |
|---|---|---|
| 技术栈 | Vue3 + Vite + Element Plus + Pinia + Axios | P0 |
| 设计风格 | 黑白灰极简（#1f1f1f / #f5f5f5）+ 卡片式布局 | P0 |
| 移动端优先 | 响应式布局，单手可操作 | P0 |
| 图表 | ECharts（进度追踪可视化） | P1 |

#### 页面开发清单

| 页面 | 路由 | 核心组件 | 优先级 |
|---|---|---|---|
| 首页 | / | 功能导航卡、今日推荐、打卡天数 | P0 |
| 注册/登录 | /login | 手机号/匿名注册、JWT 存储 | P0 |
| 体态评估 | /assessment | 分步问卷、进度条、提交按钮 | P0 |
| 评估报告 | /assessment/report | 风险等级展示、问题点列表、建议、方案入口 | P0 |
| 方案推荐 | /plans | 场景选择器、方案卡片列表 | P0 |
| 方案详情 | /plans/:id | 动作序列展示、跟练计时器、完成按钮 | P0 |
| 提醒与追踪 | /tracking | 提醒设置表单、训练日历、统计图表 | P0 |
| 我的 | /profile | 评估历史、训练记录、个人信息 | P0 |
| 智能问答 | /qa | 问答输入框、答案展示、相关方案 | P1 |

#### 前端关键交互

| 交互 | 说明 |
|---|---|
| 问卷分步提交 | 肩颈区完成后保存到 Redis 会话，再填腰背区，最终合并提交 |
| 评估结果→方案推荐 | 报告页"查看推荐方案"按钮携带评估结果跳转方案页 |
| 方案跟练 | 方案详情页展示动作序列，每个动作有倒计时，完成后自动下一个 |
| 完成打卡 | 方案跟练结束后弹出完成确认，记录到 training_log |
| 久坐提醒 | 前端 setInterval 定时弹窗，推荐对应时长的微休息方案 |
| 就医提示 | 评估高风险时用 ElMessageBox.alert 弹窗，阻断方案推荐 |

### 2.2 后端技术需求

| 需求项 | 说明 | 优先级 |
|---|---|---|
| 技术栈 | FastAPI + SQLAlchemy + uvicorn | P0 |
| 鉴权 | JWT（创建/解析/中间件） | P0 |
| 数据库 | SQLAlchemy async + MySQL 8.0 | P0 |
| 缓存 | aioredis / redis-py async | P0 |

#### API 接口清单

| 接口 | 方法 | 路径 | 说明 | 优先级 |
|---|---|---|---|---|
| 注册 | POST | /api/auth/register | 匿名ID或手机号注册 | P0 |
| 登录 | POST | /api/auth/login | 返回JWT | P0 |
| 提交评估 | POST | /api/assessment | 提交问卷答案，返回评估报告 | P0 |
| 评估历史 | GET | /api/assessment/history | 查询用户评估历史 | P0 |
| 方案推荐 | GET | /api/plans/recommend?area=&duration=&scene= | 根据场景推荐方案 | P0 |
| 方案详情 | GET | /api/plans/:id | 查询方案动作序列 | P0 |
| 方案列表 | GET | /api/plans?area=&duration=&scene= | 按条件筛选方案 | P0 |
| 记录训练 | POST | /api/training | 记录完成的方案 | P0 |
| 训练统计 | GET | /api/training/stats?period=week|month | 周/月统计 | P0 |
| 打卡天数 | GET | /api/training/streak | 连续打卡天数 | P0 |
| 提醒设置 | PUT | /api/reminder | 设置提醒间隔 | P0 |
| 提醒查询 | GET | /api/reminder | 查询提醒设置 | P0 |
| 智能问答 | POST | /api/qa | 提交问题，返回答案 | P1 |

### 2.3 Skills 代码实现

4 个 Skill 各为一个 Python 模块，放在 `skills/` 目录：

| 文件 | 功能 | 核心逻辑 |
|---|---|---|
| skills/posture_assessment.py | 体态评估评分 | 遍历答案计算总分，检查安全红线，判定风险等级 |
| skills/plan_matcher.py | 方案匹配推荐 | 按部位/时长/场景/风险等级过滤排序，取前3 |
| skills/safety_check.py | 安全边界检查 | 检查红线命中+高风险+既往史，返回是否安全 |
| skills/qa_responder.py | 智能问答 | 关键词匹配知识库，返回最佳答案 |

### 2.4 数据库实现

按 PRD §4.3 设计 6 张表，建表 SQL 放在 `project/backend/db/schema.sql`。

关键设计：
1. assessment.answers 用 JSON 存储各条目答案
2. exercise_plan.movements 用 JSON 存储动作序列
3. training_log 按 (user_id, created_at) 建联合索引
4. 方案库预置数据用 `seed_plans.sql` 初始化

### 2.5 Redis 缓存实现

| 场景 | 实现 |
|---|---|
| 热门方案缓存 | GET /api/plans/recommend 先查 Redis Hash，未命中查 RDS 后写入 |
| 问卷会话状态 | 分步提交时存 Redis Hash，TTL 30 分钟 |
| 打卡天数 | 每日首次完成训练时更新 Redis String，TTL 24 小时 |
| 问答缓存 | 问题 hash 后查 Redis String，未命中查知识库后写入 |

---

## 3. 部署方案

### 3.1 华为云资源

| 资源 | 规格 | 用途 |
|---|---|---|
| ECS | 2vCPU/2GB/40GB | 部署前后端 + Nginx |
| RDS MySQL | 通用型 2vCPU/2GB/40GB | 数据持久化 |
| DCS Redis | 单机 128MB | 缓存与会话 |

### 3.2 部署流程

```
1. ECS 安装 Docker + docker-compose
2. RDS 创建实例 + 导入 schema.sql + seed_plans.sql
3. DCS 创建 Redis 实例
4. 后端打包 Docker 镜像
5. 前端 pnpm build → dist 静态文件
6. Nginx 反代：/ → dist，/api → FastAPI
7. 配置环境变量（DB/Redis 连接信息）
8. 启动 docker-compose
9. 验证可访问
```

---

## 4. 交付物与排期

| 交付物 | 截止节点 |
|---|---|
| 前后端项目骨架 + 数据库建表 | 第 2 周末 |
| 用户注册/登录 API + 前端登录页 | 第 3 周末 |
| 评估问卷 API + 前端评估页 + 报告页 | 第 4 周末 |
| 方案推荐 API + 前端方案页 + Skills 代码 | 第 5 周末 |
| 训练追踪 + 提醒设置 API + 前端追踪页 | 第 5 周末 |
| Redis 缓存接入 + 就医提示 + 联调 | 第 6 周末 |
| Docker 部署 + 演示环境验证 | 第 7 周末 |
| 代码冻结 + 最终部署 | 第 8 周末 |

---

## 5. 协作节点

| 对接角色 | 对接内容 | 时间 |
|---|---|---|
| 专业内容角色 | 方案库 JSON、评估规则、知识库内容 | 第 2-4 周 |
| 产品角色 | 可部署代码包、环境配置清单 | 第 7 周末 |
| 产品角色 | 演示环境部署验证 | 第 7 周末 |