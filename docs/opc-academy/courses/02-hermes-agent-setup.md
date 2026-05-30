# Hermes Agent 安装与配置全攻略

> **导语**：如果说编程IDE是你的"剑"，那Hermes Agent就是你的"指挥中心"。它不是另一个AI聊天工具——它是让你通过自然语言操控整个数字工作流的中枢系统。从管理GitHub仓库到操控浏览器，从读写文件到编排多个AI子代理协同作战，Hermes Agent把"一个人+AI=一个团队"这句话变成了可执行的技术方案。本课程将带你从零开始，一步步完成Hermes Agent的安装、配置与集成，搭建属于你的一人公司指挥中心。

---

## 一、认识Hermes Agent：OPC的AI中枢

### 1.1 Hermes Agent是什么？

**Hermes Agent** 是由 Nous Research 开发的开源AI代理框架。它不是一个大模型，而是一个"模型的操作系统"——它连接大语言模型（LLM）和真实世界的工具，让AI不只是"聊天"，而是能**实际做事**。

用一句话理解：**Hermes Agent = LLM（大脑）+ 工具集（双手）+ 技能系统（技能）**

它能做什么？举几个真实的OPC场景：

- **代码项目管理**：一句话"帮我初始化一个Next.js项目，配置Tailwind和Prisma，然后推送到GitHub"——它自动完成全部操作
- **内容生产流水线**："搜索最近一周AI创业的热点话题，写一篇深度分析，生成封面图，发布到我的博客"——端到端自动化
- **多任务并行推进**：同时处理"优化网站SEO"、"回复客户邮件"、"分析上周销售数据"三个任务
- **系统运维**："检查服务器状态，如果有异常自动重启并通知我"

### 1.2 为什么选择Hermes Agent而不是其他方案？

市面上有很多AI代理方案（AutoGPT、CrewAI、LangChain Agent等），Hermes Agent的独特优势在于：

| 特性 | Hermes Agent | 其他方案 |
|------|-------------|---------|
| **本地运行** | ✅ 完全本地，数据不出你的电脑 | ❌ 多数依赖云端 |
| **工具生态** | ✅ 内置丰富的工具集（浏览器、终端、文件、GitHub等） | ⚠️ 需要自己搭建 |
| **技能系统** | ✅ 可扩展的Skills架构，社区共享 | ⚠️ 无标准化 |
| **多Agent编排** | ✅ 原生的子代理委托机制 | ⚠️ 需要额外框架 |
| **平台集成** | ✅ 飞书/微信/Telegram等多平台 | ⚠️ 需要自己开发 |
| **开源** | ✅ Apache 2.0 协议 | ⚠️ 部分商业限制 |

对于OPC创业者来说，最关键的三个优势是：**数据本地化（安全）、技能可复用（效率）、多Agent协作（规模化）**。

### 1.3 系统要求与环境准备

在开始安装之前，确保你的环境满足以下要求：

**硬件要求：**
- **CPU**：至少4核（推荐8核以上，用于多Agent并行）
- **内存**：至少8GB RAM（推荐16GB以上，大模型推理需要）
- **存储**：至少20GB可用空间（模型文件可能占用10-15GB）
- **GPU**（可选但推荐）：NVIDIA GPU with 8GB+ VRAM（用于本地模型推理）

**软件要求：**
- **操作系统**：macOS 12+ / Ubuntu 20.04+ / Windows 11（WSL2推荐）
- **Python**：3.10 或更高版本
- **Git**：2.30+
- **Node.js**（可选）：18+（部分工具集成需要）

**网络要求：**
- 稳定的互联网连接（使用云端API模型时需要）
- 如果使用本地模型（Ollama），需要能访问模型下载源

---

## 二、多种安装方式详解

### 2.1 方式一：pip 安装（推荐新手）

最简安装路径，适合大多数用户：

```bash
# 1. 创建虚拟环境（强烈建议）
python3 -m venv hermes-env
source hermes-env/bin/activate  # macOS/Linux
# .\hermes-env\Scripts\activate  # Windows

# 2. 升级pip
pip install --upgrade pip

# 3. 安装 Hermes Agent
pip install hermes-agent

# 4. 验证安装
hermes-agent --version
```

**为什么用虚拟环境？**隔离依赖冲突。Python生态中不同项目可能需要不同版本的库，虚拟环境让你每个项目独立。

### 2.2 方式二：Docker 安装（推荐有容器经验的用户）

Docker安装的优势是环境完全隔离，不污染主机系统：

```bash
# 1. 拉取镜像
docker pull nousresearch/hermes-agent:latest

# 2. 创建配置目录
mkdir -p ~/.hermes

# 3. 运行容器
docker run -d \
  --name hermes-agent \
  -v ~/.hermes:/root/.hermes \
  -v $(pwd):/workspace \
  -p 8080:8080 \
  nousresearch/hermes-agent:latest

# 4. 查看运行状态
docker logs hermes-agent
```

**Docker方式的特别注意事项：**
- `-v ~/.hermes:/root/.hermes`：挂载配置目录，持久化你的设置和技能
- `-v $(pwd):/workspace`：挂载当前工作目录，让Agent能访问你的项目文件
- 端口映射根据你的需要调整

### 2.3 方式三：源码安装（推荐高级用户/贡献者）

适合需要定制或参与开发的用户：

```bash
# 1. 克隆仓库
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 2. 安装依赖
pip install -e ".[dev]"

# 3. 运行
python -m hermes_agent
```

源码安装的好处是你可以直接修改源码，调试问题，甚至提交PR贡献代码。

### 2.4 安装后验证清单

安装完成后，逐一检查以下项：

```bash
# ✅ 检查版本
hermes-agent --version

# ✅ 检查工具列表
hermes-agent tools list

# ✅ 运行健康检查
hermes-agent health

# ✅ 测试基本对话
hermes-agent chat "你好，请介绍一下你能做什么"
```

如果以上四项都通过，恭喜你，Hermes Agent安装成功。

### 2.5 常见安装问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| `pip install` 失败 | 网络或依赖冲突 | 使用国内镜像：`pip install hermes-agent -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `command not found` | PATH未包含pip的bin目录 | 检查 `echo $PATH`，添加 `~/.local/bin` 到PATH |
| Docker端口被占用 | 8080端口已被其他服务占用 | 改用其他端口：`-p 9090:8080` |
| 权限错误 | 文件权限不足 | Docker方式检查挂载目录权限；pip方式检查虚拟环境 |
| Python版本不兼容 | Python版本过低 | 使用 `pyenv` 安装Python 3.10+ |

---

## 三、模型选择与Provider配置

### 3.1 理解模型Provider架构

Hermes Agent的Provider设计让你可以灵活选择"用什么模型驱动Agent"：

```
你的输入 → Hermes Agent → Provider层（API网关） → 实际模型
                                    ├── OpenAI API
                                    ├── Anthropic API  
                                    ├── Ollama（本地）
                                    ├── DeepSeek API
                                    └── 自定义Provider
```

### 3.2 Provider配置详解

核心配置文件位于 `~/.hermes/hermes-agent/config.yaml`（或JSON格式）。一个典型的配置示例：

```yaml
# ~/.hermes/hermes-agent/config.yaml
default_provider: anthropic

providers:
  anthropic:
    type: anthropic
    api_key: ${ANTHROPIC_API_KEY}  # 从环境变量读取
    model: claude-sonnet-4-20250514
    max_tokens: 4096
    temperature: 0.7

  openai:
    type: openai
    api_key: ${OPENAI_API_KEY}
    model: gpt-4o
    base_url: https://api.openai.com/v1

  deepseek:
    type: openai_compatible
    api_key: ${DEEPSEEK_API_KEY}
    model: deepseek-chat
    base_url: https://api.deepseek.com/v1

  ollama:
    type: ollama
    model: qwen2.5:14b
    base_url: http://localhost:11434
```

### 3.3 模型选择策略：不同场景用不同模型

**选模型的核心原则：不同任务用不同模型，而非一个模型打天下。**

| 任务类型 | 推荐模型 | 理由 |
|---------|---------|------|
| 日常对话/指令分发 | Claude Sonnet / GPT-4o mini | 够快，够聪明，成本低 |
| 深度分析/长文写作 | Claude Opus / GPT-4o | 推理能力最强 |
| 代码生成与调试 | Claude Sonnet / DeepSeek Coder | 代码能力突出 |
| 本地隐私任务 | Ollama + Qwen2.5 / Llama 3 | 数据不出本地 |
| 高频低成本任务 | DeepSeek V3 / GPT-4o mini | 性价比最高 |
| 多Agent编排（Orchestrator） | Claude Sonnet / GPT-4o | 需要强指令遵循能力 |

### 3.4 API Key安全管理

**千万注意**：API Key是你钱包的钥匙，泄露可能造成巨额损失。

```bash
# ❌ 错误做法：硬编码在配置文件里
api_key: "sk-abc123def456..."

# ✅ 正确做法1：环境变量
export ANTHROPIC_API_KEY="sk-xxx"
# 配置文件引用：api_key: ${ANTHROPIC_API_KEY}

# ✅ 正确做法2：使用 .env 文件（加入 .gitignore）
echo "ANTHROPIC_API_KEY=sk-xxx" > ~/.hermes/.env
echo ".env" >> ~/.hermes/.gitignore

# ✅ 正确做法3：macOS Keychain
security add-generic-password -a hermes -s anthropic-api-key -w "sk-xxx"
```

**额外的安全措施：**
- 在API平台设置月度消费上限（建议初期设100-300元/月）
- 启用API使用通知（有异常用量时立即短信/邮件提醒）
- 定期轮换API Key（每3个月更换一次）
- 永远不要把包含Key的配置文件提交到Git仓库

---

## 四、平台集成：连接你的工作入口

### 4.1 飞书（Lark）集成

飞书是国内创业者最常用的协作平台。Hermes Agent可以直接接入飞书，让你在飞书聊天窗口中指挥Agent：

```yaml
# config.yaml 中增加飞书配置
platforms:
  feishu:
    enabled: true
    app_id: ${FEISHU_APP_ID}
    app_secret: ${FEISHU_APP_SECRET}
    verification_token: ${FEISHU_VERIFICATION_TOKEN}
    encrypt_key: ${FEISHU_ENCRYPT_KEY}  # 可选
```

**配置步骤：**
1. 登录 [飞书开放平台](https://open.feishu.cn)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 在"事件订阅"中配置请求网址（需要公网可访问的URL）
5. 订阅 `im.message.receive_v1` 事件
6. 发布应用并添加到群聊

**本地开发测试技巧**：使用 ngrok 做内网穿透：
```bash
ngrok http 8080
# 将生成的 https://xxx.ngrok.io 填入飞书的事件请求网址
```

### 4.2 微信集成

微信集成相对复杂（因为微信开放生态的限制），但有几种可行方案：

- **企业微信**：通过企业微信应用API接入，相对规范
- **个人微信（WeChat）**：通过 itchat-uos 等第三方库，但有封号风险
- **微信公众号**：通过公众号消息接口接入，最稳定但交互有限

推荐OPC创业者优先使用**企业微信方案**，稳定且合法合规。

### 4.3 Telegram集成

Telegram的Bot API最为开放友好：

```yaml
platforms:
  telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
    allowed_users:  # 白名单
      - 123456789
      - 987654321
```

配置非常简单：
1. 在Telegram中搜索 `@BotFather`，发送 `/newbot` 创建机器人
2. 获取 Bot Token
3. 填入配置，重启Agent即可

### 4.4 多平台同步策略

如果你同时使用飞书、微信、Telegram，建议的策略：

- **飞书**：作为主要工作入口，处理项目管理和团队协作（如果你有小团队）
- **Telegram**：作为个人移动端入口，在外面时快速下达任务
- **微信**：作为客户对接入口，自动回复客户常见问题

关键是：**所有平台共享同一个Agent后端**，无论在哪个平台下达任务，Agent的行为是一致的、上下文是打通的。

---

## 五、安全配置最佳实践

### 5.1 权限控制三层模型

Hermes Agent的安全架构基于三层权限控制：

```
第一层：工具权限（哪些工具可用）
  └── 第二层：路径权限（工具的访问范围）
      └── 第三层：操作确认（敏感操作需人工确认）
```

**配置示例：**

```yaml
security:
  # 第一层：工具白名单
  allowed_tools:
    - read_file
    - write_file
    - terminal
    - search_files
    - web_search
    # 不包含 delete_file, git_push 等敏感操作

  # 第二层：路径限制
  workspace_root: /Users/yourname/Projects  # 只能访问这个目录
  forbidden_paths:
    - ~/.ssh
    - ~/.aws
    - /etc
    - /System

  # 第三层：需要确认的操作
  require_confirmation:
    - git push
    - rm -rf
    - pip install
    - 金额大于100元的支付操作
```

### 5.2 密钥管理的"零硬编码"原则

**黄金法则**：所有敏感信息（API Key、Token、密码）只存在于环境变量或密钥管理服务中，绝不出现在配置文件、代码或日志中。

推荐方案分级：

| 级别 | 方案 | 适用场景 |
|------|------|---------|
| 基础 | `.env` + `.gitignore` | 个人开发者 |
| 进阶 | macOS Keychain / 1Password CLI | 需要跨设备同步 |
| 专业 | HashiCorp Vault / AWS Secrets Manager | 多项目/团队协作 |
| 极致 | 硬件安全密钥（YubiKey）+ PGP | 最高安全需求 |

### 5.3 日志与审计

开启审计日志，记录Agent的所有操作：

```yaml
audit:
  enabled: true
  log_level: info
  log_path: ~/.hermes/logs/
  retention_days: 30
  redact_patterns:  # 自动脱敏
    - "sk-[a-zA-Z0-9]{32,}"
    - "Bearer [a-zA-Z0-9._\\-]+"
    - "[0-9]{16,19}"  # 信用卡号
```

定期检查日志中的异常操作模式。建议每周花5分钟过一遍。

### 5.4 网络隔离与本地优先

一个容易被忽视的安全维度：**网络隔离**。

- **本地模型优先**：敏感数据处理的场景，使用Ollama等本地模型，数据不出你的电脑
- **VPN/代理隔离**：访问外部API时走独立网络通道
- **API网关**：如果向客户提供Agent服务，在Agent前加一层API网关做认证和限流

---

## 六、性能调优与故障排查

### 6.1 性能监控指标

关注这些关键指标，帮你发现瓶颈：

- **TTFT（Time to First Token）**：从发送指令到Agent开始响应的时间。理想值 < 3秒
- **工具调用耗时**：每个工具调用的平均耗时。终端命令通常 < 5秒，网络请求 < 10秒
- **上下文窗口使用率**：对话历史占模型上下文窗口的比例。超过70%应考虑压缩或切换长上下文模型
- **并发处理能力**：同时处理多个任务时的响应延迟。如果线性增长说明模型/API成了瓶颈

### 6.2 常见性能问题

| 症状 | 诊断方法 | 解决方案 |
|------|---------|---------|
| 响应越来越慢 | 检查上下文窗口使用率 | 定期 `/clear` 或设置自动上下文压缩 |
| 工具调用超时 | 查看具体哪个工具慢 | 为慢工具设置更合理的超时时间 |
| API费用爆炸 | 查看Token用量统计 | 切换到更便宜的模型处理简单任务 |
| 内存占用过高 | `htop` 或活动监视器 | 减小上下文窗口，或升级内存 |
| Agent"忘记"前面说过的话 | 上下文窗口溢出 | 使用 `summarize` 技能压缩历史 |

### 6.3 调优建议

**模型层面：**
- 指令型任务（编排、路由）用能力中等但速度快的模型（如 GPT-4o mini）
- 创造性任务（写作、分析）用能力最强的模型
- 敏感任务用本地模型，牺牲一点质量换取隐私

**系统层面：**
- macOS用户检查"内存压力"：绿色=正常，黄色=注意，红色=需要升级
- 使用SSD而非HDD存储模型文件，加载速度差距可达10倍
- 定期清理 `~/.hermes/logs/` 中的旧日志

### 6.4 建立你的"紧急恢复预案"

任何系统都可能出问题。准备工作：

1. **备份配置文件**：`cp ~/.hermes/config.yaml ~/backup/hermes-config-$(date +%Y%m%d).yaml`
2. **记录依赖版本**：`pip freeze > requirements-freeze.txt`
3. **准备备用模型**：在主Provider不可用时自动降级到备用
4. **监控脚本**：一个简单的cron脚本，每5分钟检查Agent是否存活

---

## 附：OPC实战——从安装到第一个任务的30分钟速通

光说不练假把式。这部分我们以一个OPC创业者的真实需求为例，演示从零到产出第一个成果的完整流程。

**场景**：你是一位独立开发者，正在开发一个SaaS产品。你想让Hermes Agent帮你完成一件事：**搜索过去一周关于你所在赛道（假设是"AI代码审查工具"）的最新动态，写一份竞品分析简报，并保存为Markdown文件。**

整个流程30分钟内完成，下面是每一步的详细操作。

**Step 1：安装（5分钟）**

```bash
python3 -m venv hermes-env && source hermes-env/bin/activate
pip install hermes-agent
```

安装完成后：
```bash
hermes-agent --version  # 确认安装成功
```

**Step 2：配置模型（5分钟）**

创建 `~/.hermes/config.yaml`：

```yaml
default_provider: anthropic
providers:
  anthropic:
    type: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    model: claude-sonnet-4-20250514
```

设置环境变量：
```bash
export ANTHROPIC_API_KEY=sk-ant-***
```

**Step 3：第一次对话（5分钟）**

启动Agent，直接描述你的需求：

> "帮我做一件事：搜索AI代码审查工具赛道过去一周的最新动态和竞品信息，整理成一份竞品分析简报。格式要求：Markdown，包含（1）本周重要动态（2）主要竞品更新（3）市场趋势判断（4）对我方产品的建议。保存到 /Users/me/Projects/competitive-analysis.md"

Agent会自动调用web_search工具搜索信息，然后用AI分析整理，最后写入文件。

**Step 4：审查与迭代（10分钟）**

打开生成的文件，你会看到一份结构化的竞品分析。如果你发现某个部分不够深入，直接追加指令：

> "第2部分竞品分析不够详细，请针对Cursor和GitHub Copilot这两个竞品，补充它们最近一个月的更新内容和技术路线差异"

Agent会重新搜索这两个竞品的具体信息，补充到文件中。**注意：它是在原文件基础上修改，而不是重写整个文件。**

**Step 5：建立自动化（5分钟）**

你发现这个竞品分析每周都要做。与其每次都手动触发，不如写入一个cron任务：

```bash
# 每周一早上8点自动执行
0 8 * * 1 hermes-agent task "进行AI代码审查工具赛道的每周竞品分析，保存到 ~/Reports/competitive-$(date +%Y%W).md"
```

从这一刻起，每周一的竞品分析报告会自动出现在你的文件夹里。**你花了30分钟做第一次，然后用一个cron命令让它永久自动化。**

**这个流程的本质**：不是"用了AI工具"，而是"建立了AI工作流"。第一次你手把手教Agent怎么做，第二次开始它自己跑。OPC的效率杠杆，就体现在这个"第一次"到"第N次"的跃迁中。

---

## 小结

Hermes Agent是你作为OPC创业者的"数字指挥中心"。它的安装并不复杂——如果你熟悉命令行，30分钟足以完成从零到可用的全过程。真正需要投入时间的是：选择合适的模型组合、做好安全配置、根据你的业务场景做平台集成。

记住这个优先级：**先跑通（pip install）→ 再跑稳（安全+配置）→ 最后跑优（平台集成+性能调优）**。不要试图一步到位，让Agent在实际使用中逐步完善。

---

## 七、远程部署与移动访问

### 7.1 服务器部署方案

当你在外面、电脑没开机时想用Agent怎么办？把它部署到一台VPS上：

```bash
# 方案A：直接 pip 安装到服务器
ssh your-server
python3 -m venv hermes-env && source hermes-env/bin/activate
pip install hermes-agent
# 配置好 config.yaml 后
hermes-agent serve --port 8080 --host 0.0.0.0
```

**服务器选型建议：**
- 入门级（个人用）：2核4G，月费约40-60元（阿里云/腾讯云轻量应用服务器）
- 推荐级（多Agent并发）：4核8G，月费约100-150元
- 如果用量不大，可以用家里的旧电脑+内网穿透方案，零额外成本

### 7.2 远程访问安全配置

把Agent暴露到公网必须做好安全：

```yaml
# 安全配置扩展
remote:
  auth:
    type: bearer_token  # 或 api_key
    token: ${HERMES_REMOTE_TOKEN}
  tls:
    enabled: true
    cert_path: /etc/letsencrypt/live/yourdomain/fullchain.pem
    key_path: /etc/letsencrypt/live/yourdomain/privkey.pem
  ip_whitelist:  # 可选白名单
    - "你的家庭/办公室公网IP"
  rate_limit:
    requests_per_minute: 30
```

**最低安全底线**（至少做到这三条）：
1. **必须启用HTTPS**（用 Let's Encrypt 免费证书）
2. **必须设置强认证Token**（32位以上随机字符串）
3. **必须配置访问限流**（防止暴力破解和滥用）

### 7.3 移动端访问方案

Agent部署到服务器后，通过飞书/Telegram在手机上随时指挥它。这是OPC创业者最常用的模式——你在咖啡馆、机场、甚至度假时，Agent依然在服务器上忠诚工作。

**三种移动端方案对比：**

| 方案 | 适用场景 | 优势 | 局限 |
|------|---------|------|------|
| 飞书手机App | 日常任务下达+查看结果 | 最自然，已有工作流 | 需要飞书开放平台配置 |
| Telegram Bot | 快速查询+通知推送 | 配置最简单 | 国内需梯子 |
| Web界面 | 复杂操作+多轮对话 | 功能最全 | 手机浏览器体验一般 |

**实践建议**：主力用飞书（日常任务），备用Telegram（当飞书出问题时），关键通知同时推送两个渠道。这样就建立了一个简单的"高可用通知体系"。

### 7.4 系统服务化：开机自启+崩溃自动重启

不管在本地Mac还是远程服务器上，你都不希望每次手动启动Agent：

**macOS（本地）——LaunchAgent方案：**
```bash
# 创建 ~/Library/LaunchAgents/com.hermes.agent.plist
cat > ~/Library/LaunchAgents/com.hermes.agent.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hermes.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/hermes-env/bin/hermes-agent</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF
launchctl load ~/Library/LaunchAgents/com.hermes.agent.plist
```

**Linux服务器——systemd方案：**
```bash
sudo cat > /etc/systemd/system/hermes-agent.service << 'EOF'
[Unit]
Description=Hermes Agent Service
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/home/youruser/hermes-env/bin/hermes-agent serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable --now hermes-agent
```

设置好之后，Agent会像一个可靠的员工——永远在线、崩溃自动重启、开机自启。你只需偶尔检查日志确认一切正常。

---

## 小结

Hermes Agent是你作为OPC创业者的"数字指挥中心"。它的安装并不复杂——如果你熟悉命令行，30分钟足以完成从零到可用的全过程。真正需要投入时间的是：选择合适的模型组合、做好安全配置、根据你的业务场景做平台集成。

记住这个优先级：**先跑通（pip install）→ 再跑稳（安全+配置+服务化）→ 最后跑优（平台集成+性能调优+远程部署）**。不要试图一步到位，让Agent在实际使用中逐步完善。

---

## 思考题

1. 你的工作场景中，哪些任务是"重复性高、规则明确"的？这些是Agent最先接管的候选
2. 画一张你的"数字工作流地图"：从获取信息→处理信息→产出结果→发布分发，Agent能在哪些节点介入？
3. 如果你的API Key泄露了，你的最大损失可能是什么？你现在的密钥管理方案能抵御这个风险吗？
4. 对比一下你每月在AI工具上的总花费（包括ChatGPT Plus、Cursor等），估算如果全面使用Hermes Agent+API，总费用是增加还是减少？
5. 假如你下周一要去旅行一周，只带手机。你需要提前做哪些配置，才能确保在外面也能像在电脑前一样指挥Agent工作？
