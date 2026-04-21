# OPC Platform

一站式OPC（一人公司）赋能平台，连接、展示、赋能全球独立创业者。

## 🚀 项目概述

OPC Platform 是一个专注于服务独立创业者（One Person Company）的综合平台，提供项目对接、技能匹配、学习成长、健康管理等全方位服务。

## ✨ 核心功能

### 1. 用户系统 ✅
- 用户注册/登录（JWT认证）
- 个人资料管理
- 技能标签系统
- 权限管理（用户/导师/管理员）

### 2. 揭榜挂帅（项目对接）✅
- 67个AI项目展示
- 智能项目匹配
- 在线投标功能
- 项目筛选与搜索

### 3. 智能匹配算法 ✅
- 基于技能的项目推荐
- 用户与项目智能匹配
- 导师匹配推荐
- 匹配分数计算

### 4. 支付系统 ✅
- 订单管理
- 支付记录
- 退款功能
- 发票管理

### 5. OPC学院 ✅
- 精品课程展示
- 导师匹配
- 学习路径
- 技能认证

### 6. 健康管理 ✅
- 运动打卡
- 健康数据追踪
- 排行榜系统
- 成就系统

### 7. 超级个体（AI Agent）✅
- SecondMe数字分身
- AI Agent对话
- A2A协作架构

### 8. 名人堂 ✅
- 传奇人物展示
- 商业哲学DNA
- AI对话功能

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python 3.9+)
- **数据库**: PostgreSQL + SQLAlchemy ORM
- **认证**: JWT + bcrypt
- **API**: RESTful API

### 前端
- **技术**: 原生HTML/CSS/JavaScript
- **设计**: 深色主题，响应式布局
- **移动端**: 完整移动端支持

### 部署
- **平台**: Render.com
- **数据库**: PostgreSQL
- **域名**: 自定义域名支持

## 📦 安装与运行

### 环境要求
- Python 3.9+
- PostgreSQL
- pip

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/MoKangMedical/opc-platform.git
cd opc-platform
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置数据库**
```bash
# 创建PostgreSQL数据库
createdb opc_platform

# 设置环境变量（可选）
export DATABASE_URL=postgresql://user:password@localhost/opc_platform
```

4. **启动服务**
```bash
python start.py
```

服务将在 http://localhost:8000 启动

## 🔌 API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

#### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/me` - 更新用户信息
- `POST /api/auth/change-password` - 修改密码

#### 用户管理
- `GET /api/users/{user_id}` - 获取用户信息
- `GET /api/users/` - 获取用户列表
- `PUT /api/users/{user_id}/role` - 更新用户角色（管理员）
- `PUT /api/users/{user_id}/status` - 更新用户状态（管理员）

#### 项目相关
- `GET /api/projects` - 获取项目列表
- `GET /api/projects/{project_id}` - 获取项目详情
- `POST /api/projects/{project_id}/bid` - 提交投标
- `GET /api/projects/{project_id}/bids` - 获取项目投标

#### 匹配算法
- `GET /api/matching/users/me/recommended-projects` - 获取推荐项目
- `GET /api/matching/users/me/recommended-mentors` - 获取推荐导师
- `GET /api/matching/projects/{project_id}/users` - 为项目匹配用户
- `GET /api/matching/stats` - 获取匹配统计

#### 支付系统
- `POST /api/payment/orders` - 创建订单
- `GET /api/payment/orders/{order_no}` - 获取订单详情
- `GET /api/payment/orders` - 获取用户订单列表
- `POST /api/payment/payments` - 创建支付
- `POST /api/payment/refunds` - 创建退款

#### 其他模块
- `GET /api/academy/courses` - 获取课程列表
- `GET /api/health/records` - 获取健康记录
- `GET /api/legends` - 获取名人堂列表
- `GET /api/agents` - 获取Agent列表

## 📱 移动端支持

平台已完整支持移动端访问，包括：
- 响应式布局设计
- 移动端底部导航栏
- 触摸优化交互
- 移动端表单优化

## 🧪 测试

运行API测试脚本：
```bash
python test_api.py
```

## 📄 项目结构

```
opc-platform/
├── app/                    # 后端应用
│   ├── main.py            # FastAPI主入口
│   ├── database.py        # 数据库配置
│   ├── models.py          # 数据模型
│   ├── routes/            # API路由
│   │   ├── auth.py        # 认证API
│   │   ├── users.py       # 用户管理API
│   │   ├── projects.py    # 项目API
│   │   ├── matching.py    # 匹配算法API
│   │   ├── payment.py     # 支付API
│   │   └── ...            # 其他模块
│   ├── services/          # 业务逻辑
│   │   ├── matching.py    # 匹配算法服务
│   │   └── payment.py     # 支付服务
│   └── middleware/        # 中间件
│       └── auth.py        # 认证中间件
├── docs/                  # 前端文件
│   ├── index.html         # 首页
│   ├── platform.html      # 平台页
│   ├── login.html         # 登录页
│   ├── register.html      # 注册页
│   ├── profile.html       # 个人资料页
│   └── mobile.js          # 移动端优化脚本
├── data/                  # 数据文件
├── requirements.txt       # Python依赖
├── start.py              # 启动脚本
├── test_api.py           # API测试脚本
└── README.md             # 项目说明
```

## 🎯 路线图

### Phase 1 - 核心平台 ✅ 已完成
- ✅ 用户系统
- ✅ 项目展示
- ✅ 智能匹配
- ✅ 支付系统
- ✅ 移动端支持

### Phase 2 - 功能增强 🔲 进行中
- 🔲 微信小程序
- 🔲 更多支付方式
- 🔲 消息通知系统
- 🔲 数据分析面板

### Phase 3 - 社区生态 🔲 计划中
- 🔲 OPC社区论坛
- 🔲 协作空间
- 🔲 知识图谱
- 🔲 AI网络

### Phase 4 - 全球化 🔲 计划中
- 🔲 多语言支持
- 🔲 海外市场
- 🔲 国际支付
- 🔲 开放API

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

- 项目负责人: linzhang
- GitHub: https://github.com/MoKangMedical/opc-platform

## 📄 许可证

MIT License

---

**一个人的公司，无限可能** 🚀

## 📐 理论基础

> **Harness理论**：在AI领域，Harness（环境设计）比模型本身更重要。优秀的Harness设计能使性能提升64%。

> **红杉论点**：从卖工具到卖结果。
