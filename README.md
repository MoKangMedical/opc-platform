# OPC Platform — 统一赋能平台

一站式OPC（One Person Company）统一平台，合并了 7 个核心子项目，为独立创业者提供项目对接、技能匹配、在线学习、健康管理、社群互动的完整生态。

## 🚀 平台概述

OPC Platform 是 MoKangMedical 生态的核心枢纽，整合了以下模块：

- **揭榜挂帅**（政府项目+供需对接）
- **超级个体**（AI Agent + SecondMe数字分身）
- **名人堂**（传奇人物 + 商业哲学）
- **OPC学院**（6门课程 + 38模块学习体系）
- **健康管理**（运动打卡 + 数据追踪）
- **社区联盟**（创业者联盟 + 交流互动）
- **同步中心**（多仓库健康检查 + 自动同步）
- **微信小程序**（OPC 的淘宝交易、培训和信息入口）

## ✨ 核心功能

### 1. 用户系统
- 注册/登录（JWT 认证）
- 个人资料管理 + 技能标签
- 权限管理（用户/导师/管理员）

### 2. 揭榜挂帅（项目对接+政府项目）
- 67个AI项目展示 + 智能匹配
- **政府项目**（揭榜挂帅）：行业分类、预算筛选、申报流程、倒计时
- 供需对接：项目发布、投标、匹配评分

### 3. 评价系统
- 多维评分：质量/沟通/及时性/专业度
- 用户信誉体系
- 评价统计

### 4. OPC 学院
- 6门精品课程，38个学习模块
- 课程：60天启动实战 / 内容创作 / 销售转化 / AI赋能 / 个人品牌 / 规模化增长
- 导师匹配 + 学习路径 + 技能认证

### 5. 健康管理
- 运动打卡 + 健康数据追踪
- 排行榜 + 成就系统

### 6. 超级个体（AI Agent）
- SecondMe 数字分身
- AI Agent 对话
- A2A 协作架构

### 7. 名人堂 + 社区
- 传奇人物展示 + DNA 商业哲学
- 创业者联盟 + 社区互动
- AI 对话功能

### 8. 同步中心
- 多仓库健康状态检查
- 自动同步引擎
- 同步状态报告

### 9. 支付系统
- 订单管理 + 支付记录
- 退款 + 发票管理

### 10. 微信小程序
- 首页：OPC 交易、培训、信息三大入口
- 交易：知识资产、服务能力、订阅意向
- 学院：OPC 课程和学习路径
- 信息：政策、案例、活动、项目机会
- 我的：订阅记录、认证入口、KnoVault H5 链接

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python 3.9+) |
| 数据库 | PostgreSQL + SQLAlchemy ORM |
| 认证 | JWT + bcrypt |
| 前端 | 原生 HTML/CSS/JavaScript，深色主题，响应式 |
| 部署 | Render.com / 自托管 |

## 📦 快速开始

```bash
# 克隆
git clone https://github.com/MoKangMedical/opc-platform.git
cd opc-platform

# 安装依赖
pip install -r requirements.txt

# 启动（SQLite模式，开箱即用）
python start.py

# API文档: http://localhost:8000/docs
# 前端入口: http://localhost:8000
```

## 🔌 API 端点

| 模块 | 前缀 | 说明 |
|------|------|------|
| 认证 | `/api/auth` | 注册/登录/密码 |
| 用户 | `/api/users` | 用户CRUD/角色管理 |
| 项目 | `/api/projects` | 项目CRUD/投标 |
| 政府项目 | `/api/government` | 揭榜挂帅/行业/申报 |
| 匹配 | `/api/matching` | 智能推荐/匹配分 |
| 学院 | `/api/academy` | 课程/导师/学习 |
| 健康 | `/api/health` | 运动记录/排行 |
| 社区 | `/api/community` | 帖子/互动 |
| 名人堂 | `/api/legends` | 人物/哲学/DNA |
| Agent | `/api/agents` | AI Agent管理 |
| 评价 | `/api/reviews` | 多维评分/统计 |
| 支付 | `/api/payment` | 订单/支付/发票 |
| 同步 | `/api/sync` | 仓库健康/同步 |

## 📂 项目结构

```
opc-platform/
├── app/                         # 后端
│   ├── main.py                  # FastAPI 主入口（v3.0.0）
│   ├── database.py              # 数据库配置
│   ├── models.py                # 数据模型（15+表）
│   ├── routes/                  # 14个路由模块
│   │   ├── academy.py           # 学院
│   │   ├── agents.py            # AI Agent
│   │   ├── auth.py              # 认证
│   │   ├── chat.py              # 聊天
│   │   ├── community.py         # 社区
│   │   ├── government.py        # 政府项目 ⭐
│   │   ├── health.py            # 健康
│   │   ├── matching.py          # 匹配算法
│   │   ├── payment.py           # 支付
│   │   ├── projects.py          # 项目
│   │   ├── realtime_chat.py     # 实时聊天
│   │   ├── reviews.py           # 评价系统 ⭐
│   │   ├── secondme.py          # 数字分身
│   │   ├── sync.py              # 同步中心 ⭐
│   │   └── users.py             # 用户管理
│   ├── services/                # 业务引擎
│   │   ├── sync_engine.py       # 同步引擎 ⭐
│   │   ├── health_checker.py    # 健康检查 ⭐
│   │   ├── matching.py          # 匹配逻辑
│   │   └── payment.py           # 支付服务
│   └── middleware/
├── docs/                        # 前端（19个页面）
│   ├── index.html               # 入口
│   ├── platform.html            # 平台主页
│   ├── home.html                # 生态展示（68项目）⭐
│   ├── government.html          # 揭榜挂帅
│   ├── academy.html             # 学院
│   ├── community.html           # 社区
│   ├── legends.html             # 名人堂
│   ├── health.html              # 健康
│   ├── chat.html                # 聊天
│   └── ...
├── miniprogram/                 # 微信小程序
│   ├── app.json                 # 小程序页面与 tab 配置
│   ├── pages/home               # 首页
│   ├── pages/market             # OPC 淘宝交易
│   ├── pages/asset-detail       # 知识资产详情
│   ├── pages/training           # OPC 学院
│   ├── pages/info               # 信息平台
│   ├── pages/profile            # 我的 OPC
│   └── utils/data.js            # Demo 数据
├── data/                        # 数据
│   ├── courses/                 # 6门课程38模块 ⭐
│   ├── toolkits/                # 工具箱
│   ├── experts/                 # 专家库
│   ├── resources/               # 资源
│   └── homepage-data.json       # 展示数据
├── scripts/                     # 工具脚本
├── requirements.txt
├── start.py
└── README.md
```

⭐ = 本次合并新增

## 🏗️ 合并记录

OPC Platform v3.0.0 合并了以下子项目：

| 子项目 | 合并内容 | 状态 |
|--------|----------|------|
| opcplatform | 6门课程 + 38模块 + 工具包 | ✅ 已合并 |
| opc-marketplace | 政府项目API + 评价系统 | ✅ 已合并 |
| opc-homepage | 生态展示首页（68项目） | ✅ 已合并 |
| opc-sync-hub | 同步引擎 + 健康检查 | ✅ 已合并 |
| opc-alliance | 创业者联盟（前端已集成） | ✅ 已合并 |
| opc-legends | 名人堂（前端已集成） | ✅ 已合并 |

原6个子仓库内容已完全整合至 opc-platform，建议归档。

## 🎯 路线图

- ✅ Phase 1：核心平台（用户/项目/匹配/支付）
- ✅ Phase 2：学院+名人堂+社区+Agent
- ✅ Phase 3：7项目统一合并（v3.0.0）
- ✅ Phase 4：微信小程序 MVP
- 🔲 Phase 4.1：微信登录、后端 API、交易状态同步和数据分析面板
- 🔲 Phase 5：多语言 + 海外市场

## 📞 联系方式

- 负责人：linzhang
- GitHub：https://github.com/MoKangMedical/opc-platform
- 域名：opcplatform.cn

---

**一个人的公司，无限可能** 🚀
