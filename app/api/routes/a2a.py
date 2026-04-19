"""
OPC SuperAgent - A2A API Routes
WebSocket + REST API for Agent communication
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from pydantic import BaseModel

from app.services.a2a_server import (
    a2a_server, AgentCard, A2AMessage, MessageType
)
from app.services.agent_engine import get_engine, AgentProfile, SkillProfile
from app.services.secondme_connector import get_connector

router = APIRouter(prefix="/api/v1/a2a", tags=["A2A SuperAgent"])


# ---- Request/Response Models ----

class CreateAgentRequest(BaseModel):
    name: str
    owner_name: str
    avatar: str = "🤖"
    role: str = ""
    organization: str = ""
    skills: List[str] = []
    bio: str = ""
    secondme_user_id: Optional[str] = None

class SendMessageRequest(BaseModel):
    sender_id: str
    receiver_id: str = ""
    content: str
    message_type: str = "user_message"
    metadata: dict = {}

class MatchRequest(BaseModel):
    skills: List[str]
    top_k: int = 10

class ProjectMatchRequest(BaseModel):
    project_code: str
    top_k: int = 5


# ---- REST Endpoints ----

@router.get("/agents")
async def list_agents():
    """获取所有在线Agent"""
    return {
        "agents": a2a_server.get_online_agents(),
        "stats": a2a_server.get_stats(),
    }


@router.post("/agents")
async def create_agent(req: CreateAgentRequest):
    """创建新Agent"""
    # 如果关联了SecondMe，先创建数字分身
    if req.secondme_user_id:
        connector = get_connector()
        sm_card = await connector.create_agent_from_secondme(req.secondme_user_id)
        if sm_card:
            card = AgentCard(**sm_card)
            a2a_server.register_agent(card)
            return {"agent": card.to_dict(), "source": "secondme"}

    # 手动创建
    card = AgentCard(
        agent_id=f"opc_{uuid.uuid4().hex[:8]}",
        name=req.name,
        owner_name=req.owner_name,
        avatar=req.avatar,
        role=req.role,
        organization=req.organization,
        skills=req.skills,
        bio=req.bio,
    )
    a2a_server.register_agent(card)
    return {"agent": card.to_dict(), "source": "manual"}


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取Agent详情"""
    agent = a2a_server.agents.get(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return {"agent": agent.to_dict()}


@router.post("/agents/{agent_id}/deactivate")
async def deactivate_agent(agent_id: str):
    """停用Agent"""
    a2a_server.unregister_agent(agent_id)
    return {"status": "ok"}


# ---- Matching Endpoints ----

@router.post("/match/agent-to-projects")
async def match_agent_to_projects(req: MatchRequest):
    """Agent匹配项目"""
    engine = get_engine()
    agent = AgentProfile(
        agent_id="temp",
        name="Temp",
        owner_name="Temp",
        skills=[SkillProfile(name=s, level=0.8) for s in req.skills],
    )
    matches = engine.match_agent_to_projects(agent, top_k=req.top_k)
    return {
        "matches": [
            {
                "project_id": m.project_id,
                "project_title": m.project_title,
                "publisher": m.publisher,
                "match_score": m.match_score,
                "matched_skills": m.matched_skills,
                "missing_skills": m.missing_skills,
                "recommendation": m.recommendation,
                "budget": m.budget_display,
            }
            for m in matches
        ]
    }


@router.post("/match/project-to-agents")
async def match_project_to_agents(req: ProjectMatchRequest):
    """项目匹配Agent"""
    engine = get_engine()
    agents = [
        AgentProfile(
            agent_id=a.agent_id,
            name=a.name,
            owner_name=a.owner_name,
            skills=[SkillProfile(name=s) for s in a.skills],
        )
        for a in a2a_server.agents.values()
        if a.status != "offline"
    ]
    results = engine.match_project_to_agents(req.project_code, agents, req.top_k)
    return {
        "matches": [
            {
                "agent_id": agent.agent_id,
                "agent_name": agent.name,
                "match_score": score,
                "matched_skills": skills,
            }
            for agent, score, skills in results
        ]
    }


@router.get("/skills/suggestions")
async def skill_suggestions(skills: str = Query(..., description="逗号分隔的技能列表")):
    """推荐可拓展技能"""
    engine = get_engine()
    skill_list = [s.strip() for s in skills.split(",")]
    suggestions = engine.get_skill_suggestions(skill_list)
    return {"current": skill_list, "suggestions": suggestions}


@router.get("/stats")
async def get_stats():
    """获取平台统计"""
    engine = get_engine()
    return {
        "a2a": a2a_server.get_stats(),
        "matching": engine.get_stats(),
    }


# ---- WebSocket Endpoint ----

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """A2A WebSocket 连接"""
    await websocket.accept()

    # 注册连接
    if agent_id not in a2a_server.agents:
        # 自动创建Agent
        card = AgentCard(
            agent_id=agent_id,
            name=f"Agent-{agent_id[:8]}",
            owner_name="Unknown",
        )
        a2a_server.register_agent(card)

    # 发送当前在线Agent列表
    await websocket.send_json({
        "jsonrpc": "2.0",
        "method": "agents_list",
        "params": {
            "agents": a2a_server.get_online_agents(),
            "stats": a2a_server.get_stats(),
        },
        "id": str(uuid.uuid4()),
    })

    # 处理连接
    await a2a_server.handle_connection(websocket, agent_id)


# ---- SecondMe Integration ----

@router.get("/secondme/profile")
async def secondme_profile(user_id: str = "2268309"):
    """获取SecondMe数字分身"""
    connector = get_connector()
    profile = await connector.get_user_profile(user_id)
    if profile:
        return {"profile": profile.__dict__}
    raise HTTPException(404, "Profile not found")


@router.post("/secondme/create-agent")
async def create_from_secondme(user_id: str = "2268309"):
    """从SecondMe创建Agent"""
    connector = get_connector()
    card = await connector.create_agent_from_secondme(user_id)
    if card:
        agent = AgentCard(**card)
        a2a_server.register_agent(agent)
        return {"agent": agent.to_dict()}
    raise HTTPException(500, "Failed to create agent from SecondMe")


@router.post("/secondme/chat")
async def chat_secondme(route: str = "xiaolin110", message: str = ""):
    """与SecondMe数字分身对话"""
    connector = get_connector()
    response = await connector.chat_with_secondme(route, message)
    if response:
        return {"response": response}
    return {"response": "数字分身暂时无法回复，请稍后再试。"}
