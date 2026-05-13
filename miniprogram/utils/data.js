const assets = [
  {
    id: "asset-growth-audit",
    title: "AI 出海增长审计报告包",
    type: "Document / Report",
    seller: "Lina OPC Studio",
    verified: true,
    promise: "帮助 AI SaaS 和独立站团队诊断增长漏斗、广告账户和邮件转化路径。",
    preview: "开放摘要、目录、样例页和最近一次更新说明；正文仅对活跃订阅者可见。",
    mode: "AI-assisted",
    price: "0.018 MON",
    duration: "30 天",
    version: "v1.4",
    rating: "4.9",
    subscriptions: 37,
    tags: ["增长", "报告", "出海"],
    trust: ["Verified OPC", "v1.4 version hash", "37 subscriptions"]
  },
  {
    id: "asset-monad-bd",
    title: "Monad 生态 BD 知识库",
    type: "Template / Methodology",
    seller: "Mu Research Cell",
    verified: true,
    promise: "帮助新团队快速理解 Monad 生态项目图谱、联系人分层和合作触达节奏。",
    preview: "开放 6 个样例条目和一页合作触达脚本；完整数据库按订阅访问。",
    mode: "Human-authored",
    price: "0.009 MON",
    duration: "14 天",
    version: "v2.1",
    rating: "4.8",
    subscriptions: 21,
    tags: ["BD", "Monad", "方法论"],
    trust: ["Portfolio sample approved", "v2.1 version hash", "21 subscriptions"]
  },
  {
    id: "asset-agent-eval",
    title: "中文 AI Agent 评测集",
    type: "Dataset / Annotation Pack",
    seller: "TinyBench OPC",
    verified: true,
    promise: "提供中文业务任务样本、rubric 和基线结果，用于比较 Agent 执行质量。",
    preview: "开放 20 条样例任务、字段说明和 rubric 摘要；完整数据包订阅后下载。",
    mode: "Agent-executed",
    price: "0.026 MON",
    duration: "30 天",
    version: "v0.9",
    rating: "4.7",
    subscriptions: 14,
    tags: ["数据集", "评测", "Agent"],
    trust: ["CID + annotation hash", "v0.9 dataset", "14 subscriptions"]
  }
];

const services = [
  {
    id: "svc-opc-setup",
    title: "OPC 冷启动商业诊断",
    provider: "OPC Mentor Network",
    price: "¥299 起",
    desc: "适合刚开始做一人公司的创业者，梳理定位、产品、渠道和第一笔交易路径。"
  },
  {
    id: "svc-agent-workflow",
    title: "AI Agent 工作流搭建",
    provider: "SuperAgent Studio",
    price: "¥799 起",
    desc: "把重复任务拆解成可执行 SOP，并设计可交付的 Agent workflow。"
  }
];

const courses = [
  {
    id: "course-opc-basic",
    title: "OPC 一人公司从 0 到 1",
    level: "入门",
    lessons: 12,
    duration: "3 小时",
    desc: "理解 OPC 商业模式、能力产品化、第一批客户和轻量交付。",
    tags: ["定位", "商业模式", "获客"]
  },
  {
    id: "course-ai-productivity",
    title: "AI 时代的个人生产系统",
    level: "进阶",
    lessons: 10,
    duration: "2.5 小时",
    desc: "用 AI 和 Agent 搭建研究、写作、销售、交付和复盘系统。",
    tags: ["AI", "Agent", "效率"]
  },
  {
    id: "course-trust-market",
    title: "把知识资产变成可交易商品",
    level: "实战",
    lessons: 8,
    duration: "2 小时",
    desc: "学习如何设计报告、模板、数据包、版本记录、预览和订阅定价。",
    tags: ["知识资产", "定价", "交易"]
  }
];

const infos = [
  {
    id: "info-policy",
    category: "政策",
    title: "上海独立创业者可关注的补贴与服务清单",
    summary: "整理场地、担保贷款、创业培训和人才政策的申请入口。",
    time: "今天"
  },
  {
    id: "info-case",
    category: "案例",
    title: "一个人如何用 AI 把行业报告做成订阅产品",
    summary: "从免费摘要、样例页、版本更新到结构化反馈的完整路径。",
    time: "昨天"
  },
  {
    id: "info-event",
    category: "活动",
    title: "OPC 线下共创：知识资产交易与 Agent 工作流",
    summary: "面向独立研究者、顾问、产品经理和小团队的实践工作坊。",
    time: "本周"
  }
];

const orders = [
  {
    id: "S-2401",
    title: "AI 出海增长审计报告包",
    status: "已反馈",
    value: "0.018 MON",
    chain: "Monad Testnet / 10143"
  },
  {
    id: "S-2398",
    title: "Monad 生态 BD 知识库",
    status: "已放款",
    value: "0.009 MON",
    chain: "Monad Testnet / 10143"
  }
];

module.exports = {
  assets,
  services,
  courses,
  infos,
  orders
};
