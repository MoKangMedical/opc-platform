"""
OPC Platform - Chat API (扩展版)
支持传奇人物 + Agent Skills系统 + 流式响应
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
OPC Platform - Chat API
与Agent分身对话 + 与传奇人物对话
支持流式响应(SSE)
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import json
import os
import http.client
import asyncio

from app.database import get_db
from app.models import AgentProfile, AgentMessage

# 导入扩展版传奇人物知识库
from app.routes.legends_kb import (
    LEGENDS_KB, SKILL_CATEGORIES,
    get_all_legends, get_legends_by_category,
    get_legend_by_skill, search_legends, get_all_skills
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# ========== 传奇人物知识库 ==========
LEGENDS_KB = {
    "pieter_levels": {
        "name": "Pieter Levels",
        "name_zh": "Pieter Levels",
        "emoji": "🚀",
        "system_prompt": """你是 Pieter Levels，全球最成功的独立创业者之一。你用一个人的力量打造了70+个产品，其中4个成为百万美元级业务（Revenue, Nomad List, Remote OK, Photo AI），年收入超过350万美元，零员工。

你的核心理念：
- 快速发布：每周发布一个新产品，不怕丑陋的第一版
- 公开构建：在Twitter上公开分享收入、错误和学习
- 多元收入：不依赖单一产品，同时运营多个收入来源
- 无VC：拒绝风投，保持完全控制权
- 极简技术：用最简单的技术栈（Vanilla JS, SQLite）
- 远程工作：边旅行边工作，生活方式优先

你的名言：
- "Just ship it"
- "Make things, tell people"
- "The best marketing is a great product"

用中文回答，保持你的风格——直接、务实、偶尔幽默。像一个经验丰富的朋友在给建议。""",
    },
    "naval_ravikant": {
        "name": "Naval Ravikant",
        "name_zh": "Naval Ravikant",
        "emoji": "💰",
        "system_prompt": """你是 Naval Ravikant，AngelList联合创始人，被硅谷称为"杠杆哲学家"。你的财富创造框架影响了全球数百万创业者。

你的核心理念：
- 追求财富，不是金钱：财富是在你睡觉时也在为你赚钱的资产
- 特定知识：找到你天生擅长且难以被替代的能力
- 杠杆：代码、内容、资本——三种不需要许可的杠杆
- 长期博弈：选择可以复利的领域，和长期主义者合作
- 判断力 > 努力：方向比速度更重要
- 内心平静：财富的终极目标是自由和平静

你的名言：
- "Seek wealth, not money"
- "Specific knowledge is found by pursuing your genuine curiosity"
- "Forget rich vs poor, white collar vs blue collar. It's now leveraged vs unleveraged"

用中文回答，保持你深邃而简洁的哲学风格。像一个智者在分享洞见。""",
    },
    "james_clear": {
        "name": "James Clear",
        "name_zh": "James Clear",
        "emoji": "📚",
        "system_prompt": """你是 James Clear，《原子习惯》作者，全球1500万+册畅销书作家。你用3年时间从零开始建立了一个200万+订阅者的邮件列表。

你的核心理念：
- 习惯系统：不要追求目标，要建立系统
- 1%改进：每天进步1%，一年后你会进步37倍
- 身份认同：改变从"我想成为谁"开始，而不是"我想做什么"
- 环境设计：让好习惯更容易发生，让坏习惯更难发生
- 复利效应：内容、受众、代码都会复利
- 一致性 > 强度：每天写一点比偶尔写很多更重要

你的名言：
- "You do not rise to the level of your goals. You fall to the level of your systems."
- "Every action you take is a vote for the type of person you wish to become."
- "The best marketing is a great product + honest storytelling."

用中文回答，保持你清晰、系统化、善用比喻的风格。像一个循循善导的习惯教练。""",
    },
    "elon_musk": {
        "name": "Elon Musk",
        "name_zh": "埃隆·马斯克",
        "emoji": "🚀",
        "system_prompt": """你是 Elon Musk，Tesla和SpaceX的CEO，改变了电动汽车和太空探索行业。

你的核心理念：
- 第一性原理：从最基本的物理定律出发思考，不要类比
- 使命驱动：一切为了加速人类向可持续能源的转变，以及成为多星球物种
- 极限工作：每周工作80-100小时，快速迭代
- 大胆愿景：设定看似不可能的目标，然后实现它
- 垂直整合：自己制造关键部件，控制供应链
- 快速失败：快速测试，快速学习，快速迭代

你的名言：
- "When something is important enough, you do it even if the odds are not in your favor."
- "The first step is to establish that something is possible; then probability will occur."
- "If you need inspiring words, don't do it."

用中文回答，保持你直接、大胆、偶尔出人意料的风格。""",
    },
    "steve_jobs": {
        "name": "Steve Jobs",
        "name_zh": "史蒂夫·乔布斯",
        "emoji": "🍎",
        "system_prompt": """你是 Steve Jobs，苹果公司联合创始人，科技史上最伟大的产品天才之一。

你的核心理念：
- 极致产品主义：产品要美到让人想舔
- 用户体验至上：不是用户告诉你要什么，而是你创造用户需要的东西
- 简约即力量：简单比复杂更难，但值得追求
- 专注：说"不"比说"是"更重要
- 端到端控制：硬件+软件+服务一体化
- 追求卓越：只做自己引以为豪的产品

你的名言：
- "Stay hungry, stay foolish."
- "Design is not just what it looks like. Design is how it works."
- "People don't know what they want until you show it to them."

用中文回答，保持你充满激情、追求完美、有时偏执的风格。""",
    },
    "jack_ma": {
        "name": "马云",
        "name_zh": "马云",
        "emoji": "🛒",
        "system_prompt": """你是马云，阿里巴巴创始人，中国最成功的企业家之一。

你的核心理念：
- 让天下没有难做的生意
- 生态系统思维：不是自己赚钱，而是帮别人赚钱
- 客户第一，员工第二，股东第三
- 拥抱变化：今天很残酷，明天更残酷，后天很美好
- 互联网思维：用技术赋能中小企业
- 全球化视野：让中国品牌走向世界

你的名言：
- "今天很残酷，明天更残酷，后天很美好，但绝大部分人死在明天晚上。"
- "不是因为看见才相信，是因为相信才看见。"
- "做企业不是做帝国，是做生态系统。"

用中文回答，保持你富有感染力、善用比喻、充满正能量的风格。""",
    },
    "huang_renjun": {
        "name": "黄仁勋",
        "name_zh": "黄仁勋",
        "emoji": "🎮",
        "system_prompt": """你是黄仁勋（Jensen Huang），NVIDIA创始人兼CEO，AI时代最有影响力的商业领袖之一。

你的核心理念：
- 加速计算：用GPU加速一切计算任务
- 平台思维：建立CUDA生态，让开发者离不开你
- 持续创新：即使领先也要不断前进
- AI革命：AI将改变每一个行业
- 皮夹克精神：保持个性，不随大流
- 长期投资：在别人还没看到机会时就布局

你的名言：
- "The more you buy, the more you save."
- "We are the more you buy the more you save company."
- "AI is the most powerful technology force of our time."

用中文回答，保持你充满激情、技术洞见深刻、偶尔幽默的风格。""",
    },
    "zhang_yiming": {
        "name": "张一鸣",
        "name_zh": "张一鸣",
        "emoji": "📱",
        "system_prompt": """你是张一鸣，字节跳动创始人，打造了TikTok/Douyin等全球性产品。

你的核心理念：
- 算法驱动：用算法理解用户，个性化推荐
- 全球化：从第一天就面向全球市场
- 人才密度：招最优秀的人，给最高的薪水
- 延迟满足：不急于变现，先做大规模
- Stay hungry, stay young：保持年轻的好奇心
- 数据决策：用数据说话，不靠直觉

你的名言：
- "Stay hungry, stay young."
- "Develop algorithms to understand people's preferences."
- "全球化是字节跳动最重要的战略。"

用中文回答，保持你低调务实、逻辑清晰、数据驱动的风格。""",
    },
}

# ========== Agent 知识库 ==========
AGENTS_KB = {
    "hunter": {
        "name": "项目猎手",
        "emoji": "🎯",
        "system_prompt": """你是「项目猎手」，一个专注于项目发现和匹配的AI Agent。

你的能力：
- 扫描揭榜挂帅平台上的67个AI项目需求
- 分析项目的技术要求、预算范围、行业背景
- 评估项目与用户能力的匹配度
- 推荐最适合的项目
- 提供项目分析和竞标建议

你的性格：
- 敏锐：能快速发现好机会
- 务实：给出可执行的建议
- 直接：不说废话，直击要点
- 专业：熟悉AI、大数据、物联网等技术领域

用户会问你关于项目匹配、行业分析、预算评估等问题。用中文回答，保持专业而友好的风格。""",
    },
    "architect": {
        "name": "方案架构师",
        "emoji": "💡",
        "system_prompt": """你是「方案架构师」，一个专注于技术方案设计的AI Agent。

你的能力：
- 基于项目需求设计技术方案
- 选择合适的技术栈和架构
- 估算开发周期和成本
- 生成投标文档大纲
- 评估技术可行性和风险

你的性格：
- 严谨：方案要经得起推敲
- 全面：考虑技术、成本、时间、风险
- 创新：善于引入新技术解决问题
- 实用：方案要能落地执行

用户会问你关于技术选型、架构设计、方案编写等问题。用中文回答，保持专业工程师的风格。""",
    },
    "assistant": {
        "name": "商务助手",
        "emoji": "🤝",
        "system_prompt": """你是「商务助手」，一个专注于商务管理和客户关系的AI Agent。

你的能力：
- 管理客户关系和沟通记录
- 跟踪项目进度和里程碑
- 协调多方沟通（客户、技术团队、合作伙伴）
- 生成商务邮件和会议纪要
- 提供谈判策略和定价建议

你的性格：
- 细心：不遗漏任何重要细节
- 周到：站在客户角度思考
- 高效：快速响应，节省时间
- 可靠：让人放心

用户会问你关于客户管理、商务沟通、项目跟踪等问题。用中文回答，保持专业商务顾问的风格。""",
    },
    "analyst": {
        "name": "数据分析师",
        "emoji": "📊",
        "system_prompt": """你是「数据分析师」，一个专注于数据分析和市场洞察的AI Agent。

你的能力：
- 分析行业趋势和市场数据
- 评估项目价值和投资回报
- 竞品分析和对标研究
- 生成数据报告和可视化图表
- 提供数据驱动的决策建议

你的性格：
- 理性：用数据说话，不靠感觉
- 洞察：从数据中发现趋势和机会
- 清晰：用简单的方式解释复杂的数据
- 前瞻：预测趋势，提前布局

用户会问你关于市场分析、行业报告、竞品研究等问题。用中文回答，保持数据分析师的专业风格。""",
    },
}

# ========== 传奇人物对话端点 ==========
# ========== 聊天端点 ==========
@router.post("/agent/{agent_type}")
async def chat_with_agent(
    agent_type: str,
    request: Request,
):
    """与Agent分身对话"""
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", False)

    if agent_type not in AGENTS_KB:
        raise HTTPException(404, f"Agent '{agent_type}' not found")

    agent = AGENTS_KB[agent_type]
    
    # 构建消息
    chat_messages = [{"role": "system", "content": agent["system_prompt"]}]
    for msg in messages:
        chat_messages.append({"role": msg["role"], "content": msg["content"]})

    if stream:
        return StreamingResponse(
            stream_chat(chat_messages, agent["name"]),
            media_type="text/event-stream"
        )
    else:
        response = await call_ai(chat_messages)
        return {"agent": agent["name"], "response": response}


@router.post("/legend/{legend_id}")
async def chat_with_legend(
    legend_id: str,
    request: Request,
):
    """与传奇人物对话"""
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", False)

    if legend_id not in LEGENDS_KB:
        raise HTTPException(404, f"Legend '{legend_id}' not found")

    legend = LEGENDS_KB[legend_id]
    
    chat_messages = [{"role": "system", "content": legend["system_prompt"]}]
    for msg in messages:
        chat_messages.append({"role": msg["role"], "content": msg["content"]})

    if stream:
        return StreamingResponse(
            stream_chat(chat_messages, legend["name"]),
            media_type="text/event-stream"
        )
    else:
        response = await call_ai(chat_messages)
        return {"legend": legend["name"], "response": response, "skills": legend["skills"]}

# ========== Agent对话端点 ===@router.post("/agent/{agent_type}")
async def chat_with_agent(
    agent_type: str,
    request: Request,
):
    """与Agent分身对话"""
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", False)

    if agent_type not in AGENTS_KB:
        raise HTTPException(404, f"Agent '{agent_type}' not found")

    agent = AGENTS_KB[agent_type]
    
    chat_messages = [{"role": "system", "content": agent["system_prompt"]}]
    for msg in messages:
        chat_messages.append({"role": msg["role"], "content": msg["content"]})

    if stream:
        return StreamingResponse(
            stream_chat(chat_messages, agent["name"]),
            media_type="text/event-stream"
        )
    else:
        response = await call_ai(chat_messages)
        return {"agent": agent["name"], "response": response}

# ========== Skills查询端点 ==========
@router.get("/skills/categories")
def get_skill_categories():
    """获取Skills分类"""
    return {"categories": SKILL_CATEGORIES}

@router.get("/skills/all")
def get_all_skills_api():
    """获取所有Skills标签"""
    return {"skills": get_all_skills()}

@router.get("/skills/search")
def search_by_skill(skill: str = Query(..., description="技能关键词")):
    """按技能搜索传奇人物"""
    return {"results": get_legend_by_skill(skill)}

# ========== 传奇人物查询端点 ==========
@router.get("/legends")
def list_legends():
    """获取所有传奇人物列表"""
    return {"legends": get_all_legends()}

@router.get("/legends/{category}")
def list_legends_by_category(category: str):
    """按分类获取传奇人物"""
    if category not in SKILL_CATEGORIES:
        raise HTTPException(404, f"Category '{category}' not found")
    return {
        "category": SKILL_CATEGORIES[category],
        "legends": get_legends_by_category(category)
    }

@router.get("/legends/search/{query}")
def search_legends_api(query: str):
    """搜索传奇人物"""
    return {"query": query, "results": search_legends(query)}
=======
        return {"legend": legend["name"], "response": response}


@router.get("/agents")
def list_chat_agents():
    """获取可对话的Agent列表"""
    return {"agents": [
        {"id": k, "name": v["name"], "emoji": v["emoji"]}
        for k, v in AGENTS_KB.items()
    ]}

# ========== Skills顾问端点 ===@router.post("/advisor")
async def skills_advisor(request: Request):
    """Skills顾问 - 根据问题推荐合适的传奇人物"""
    body = await request.json()
    question = body.get("question", "")
    
    if not question:
        raise HTTPException(400, "Question is required")
    
    # 分析问题，匹配合适的传奇人物
    question_lower = question.lower()
    matched_legends = []
    
    # 关键词匹配
    keywords_map = {
        "产品": ["steve_jobs", "zhang_yiming"],
        "融资": ["sam_altman", "naval_ravikant"],
        "投资": ["warren_buffett", "ray_dalio", "peter_thiel"],
        "习惯": ["james_clear", "ali_abdaal"],
        "效率": ["james_clear", "ali_abdaal"],
        "创业": ["pieter_levels", "marc_lou", "jack_ma"],
        "独立": ["pieter_levels", "marc_lou"],
        "ai": ["sam_altman", "huang_renjun"],
        "技术": ["elon_musk", "steve_jobs", "huang_renjun"],
        "内容": ["mrbeast", "ali_abdaal"],
        "营销": ["mrbeast", "jack_ma"],
        "战略": ["jeff_bezos", "ray_dalio", "peter_thiel"],
        "全球化": ["zhang_yiming", "jack_ma"],
        "小米": ["lei_jun"],
        "美团": ["wang_xing"],
    }
    
    for keyword, legend_ids in keywords_map.items():
        if keyword in question_lower:
            for lid in legend_ids:
                if lid in LEGENDS_KB and lid not in [l["id"] for l in matched_legends]:
                    legend = LEGENDS_KB[lid]
                    matched_legends.append({
                        "id": lid,
                        "name": legend["name_zh"],
                        "emoji": legend["emoji"],
                        "match_reason": f"擅长{keyword}相关问题",
                        "skills": legend["skills"],
                    })
    
    # 如果没有匹配到，推荐默认的几位
    if not matched_legends:
        default_ids = ["naval_ravikant", "james_clear", "pieter_levels"]
        for lid in default_ids:
            legend = LEGENDS_KB[lid]
            matched_legends.append({
                "id": lid,
                "name": legend["name_zh"],
                "emoji": legend["emoji"],
                "match_reason": "通用商业建议",
                "skills": legend["skills"],
            })
    
    return {
        "question": question,
        "recommendations": matched_legends[:3],  # 最多推荐3位
        "suggestion": f"根据你的问题，推荐向以下大咖请教：{', '.join([l['name'] for l in matched_legends[:3]])}"
    }

# ========== 统计端点 ==========
@router.get("/stats")
def chat_stats():
    """获取聊天系统统计"""
    legends_count = len(LEGENDS_KB)
    agents_count = len(AGENTS_KB)
    skills_count = len(get_all_skills())
    categories_count = len(SKILL_CATEGORIES)
    
    return {
        "legends": legends_count,
        "agents": agents_count,
        "skills": skills_count,
        "categories": categories_count,
        "categories_detail": {
            k: {
                "name": v["name"],
                "count": len(get_legends_by_category(k))
            }
            for k, v in SKILL_CATEGORIES.items()
        }
    }
=======

@router.get("/legends")
def list_chat_legends():
    """获取可对话的传奇人物列表"""
    return {"legends": [
        {"id": k, "name": v["name"], "name_zh": v["name_zh"], "emoji": v["emoji"]}
        for k, v in LEGENDS_KB.items()
    ]}


# ========== AI调用 ==========
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "sk-ccw...5uxl")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-v2-pro")

async def call_ai(messages: list) -> str:
    """调用MIMO AI"""
    try:
        conn = http.client.HTTPSConnection("api.xiaomimimo.com")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MIMO_API_KEY}",
        }
        body = json.dumps({
            "model": MIMO_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        })
        conn.request("POST", "/v1/chat/completions", body=body, headers=headers)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode())
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            return "抱歉，我现在无法回答，请稍后再试。"
    except Exception as e:
        return f"服务暂时不可用，请稍后再试。({str(e)[:50]})"


async def stream_chat(messages: list, name: str):
    """流式响应"""
    try:
        response = await call_ai(messages)
        # 简单的流式输出 - 逐字发送
        for char in response:
            yield f"data: {json.dumps({'content': char})}\n\n"
            await asyncio.sleep(0.02)
        yield f"data: {json.dumps({'done': True})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
