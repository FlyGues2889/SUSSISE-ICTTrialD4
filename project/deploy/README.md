# 华为云部署手册

目标：把「久坐肩颈腰背科学运动干预助手」部署到一台 ECS，形成可公网访问的在线演示地址（对应 PRD 验收标准 AC6）。

本地开发不需要本目录的任何文件，直接看 `project/使用指南.md`。

## 1. 资源与端口

| 资源 | 规格 | 说明 |
|------|------|------|
| ECS | 2vCPU / 2GB / 40GB，Ubuntu 22.04 或 openEuler 24.03 | 运行 Nginx + 后端 |
| RDS MySQL | 8.0，同 VPC | 业务数据 |
| DCS Redis | 单机 128MB，可选 | 配了 `REDIS_URL` 才启用，不配自动降级 |
| 安全组 | 入方向 80（演示）、22（运维） | 8001 只监听 127.0.0.1，不对外 |

## 2. 部署步骤

```bash
# 2.1 基础环境
sudo apt update && sudo apt install -y nginx python3.11 python3.11-venv git
curl -fsSL https://get.pnpm.io/install.sh | sh -

# 2.2 拉代码
sudo mkdir -p /opt && cd /opt
git clone <仓库地址> d4 && cd d4

# 2.3 后端依赖
cd project/backend
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2.4 环境变量
sudo mkdir -p /etc/d4
sudo cp project/deploy/api.env.example /etc/d4/api.env   # 在仓库根目录执行
sudo vim /etc/d4/api.env                                  # 填 RDS 地址、密码、JWT_SECRET

# 2.5 启动后端（建表与方案/知识库种子在启动时自动完成）
sudo cp project/deploy/sedentary-api.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now sedentary-api
curl http://127.0.0.1:8001/api/health        # 期望 {"status":"ok"}

# 2.6 前端构建（云模式，关闭本地 Mock）
cd /opt/d4/project/frontend
pnpm install && pnpm build:cloud
sudo mkdir -p /var/www/d4
sudo cp -r dist/* /var/www/d4/

# 2.7 Nginx
sudo cp /opt/d4/project/deploy/nginx.conf /etc/nginx/conf.d/d4.conf
sudo nginx -t && sudo systemctl reload nginx
```

`sedentary-api.service` 里的 `WorkingDirectory` 与 venv 解释器路径需按实际部署目录调整。

## 3. 演示数据（可选，推荐）

正式评审前载入演示账号，保证首屏就有趋势与打卡记录：

```bash
cd /opt/d4
project/backend/.venv/bin/python project/backend/scripts/seed_demo.py
# 重复执行会跳过已存在账号；要重建加 --reset
```

| 账号 | 内容 |
|------|------|
| 演示·小林 | 肩颈 21→18→16→14→13 分、腰背 12→9→7→5→4 分，近 7 天 6 次训练，连续打卡 5 天，45 分钟提醒 |
| 演示·高风险 | 颈部红线命中，用于演示就医提示与方案拦截 |

云模式的登录页「演示账号 / 高风险演示」走 `POST /api/auth/demo-login` 换取真实 token，不需要密码；若返回 404，说明后端版本落后，重新拉代码并重启 `sedentary-api`。

## 4. 上线验收清单

按顺序在手机与桌面各走一遍，全部通过才算部署完成：

1. `http://<ECS公网IP>/` 首屏可打开，刷新任意子路由（如 `/tracking`）不 404。
2. 注册 → 首页出现「今天建议」卡片。
3. 完成 24 题评估 → 报告显示四档风险、问题点、健康依据与下一步按钮。
4. 首页「换一组」可切换方案 → 进入跟练 → 完成打卡 → 提示「打卡成功」。
5. 「提醒与追踪」出现本周柱状、本月统计、改善趋势折线、部位关注度。
6. 「全部方案」可收藏（心形变绿）、可新建自定义方案并进入跟练。
7. 「我的 → 常见问题」提问「久坐多久需要起身活动」能命中知识库答案并标注「知识库」；范围外问题配置了 `AI_PROVIDER` 时标注「AI 回答」，未配置时返回「暂时无法回答」。
8. 高风险账号评估后首页不推荐方案，并显示就医提示。
9. 「提醒与追踪」设置 1 分钟间隔后切到首页，页内提醒仍按时弹出，最近提醒时间同步刷新。

## 5. 常见问题

- **页面空白、控制台报无法连接服务器**：`sedentary-api` 未启动或 Nginx 未反代 `/api`。先 `curl http://127.0.0.1:8001/api/health`，再 `curl http://127.0.0.1/api/health`。
- **刷新子路由 404**：缺 `try_files $uri $uri/ /index.html`。
- **推荐方案为空**：`exercise_plan` 未写入。启动日志出现「数据库初始化完成」即会补种 36 个方案；确认 RDS 账号有建表与写权限。
- **问答总是「无法回答」**：`knowledge_base` 为空，同样由启动自动补种 10 条；若仍为空检查 `db/seed_kb.sql` 是否随代码部署。
- **问答没有「AI 回答」标识**：`AI_PROVIDER` 未设为 `huawei`，或 `HUAWEI_AI_ENDPOINT` / `HUAWEI_AI_TOKEN` 为空。AI 调用失败会自动回退到知识库拒答文案，不影响主流程。
- **JWT 过期频繁**：多台后端实例需共用同一个 `JWT_SECRET`。