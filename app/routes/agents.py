"""
OPC Platform - A2A Agents API (超级个体)
Agent创建、匹配、通信
"""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
import json
import asyncio
from app.database import get_db
from app.models import AgentProfile, AgentMessage, Project, User

router = APIRouter(prefix="/api/agents", tags=["Agents"])

# ========== Agent管理 ==========
@router.get("")
def list_agents(
    agent_type: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(AgentProfile).filter(AgentProfile.is_active == is_active)
    if agent_type:
        query = query.filter(AgentProfile.agent_type == agent_type)
    agents = query.order_by(desc(AgentProfile.created_at)).all()
    return {"agents": [{
        "id": a.id, "user_id": a.user_id, "name": a.name,
        "avatar_emoji": a.avatar_emoji, "agent_type": a.agent_type,
        "description": a.description, "skills": a.skills or [],
        "is_active": a.is_active, "created_at": a.created_at.isoformat(),
    } for a in agents]}

@router.post("")
def create_agent(
    user_id: int = 1,
    name: str = "",
    avatar_emoji: str = "🤖",
    agent_type: str = "assistant",
    description: str = "",
    skills: List[str] = [],
    db: Session = Depends(get_db)
):
    agent = AgentProfile(
        user_id=user_id, name=name, avatar_emoji=avatar_emoji,
        agent_type=agent_type, description=description, skills=skills
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {"id": agent.id, "message": f"Agent '{name}' created", "agent_type": agent.agent_type}

@router.get("/{agent_id}")
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(AgentProfile).filter(AgentProfile.id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    return {
        "id": agent.id, "user_id": agent.user_id, "name": agent.name,
        "avatar_emoji": agent.avatar_emoji, "agent_type": agent.agent_type,
        "description": agent.description, "skills": agent.skills or [],
        "config": agent.config or {}, "created_at": agent.created_at.isoformat(),
    }

@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(AgentProfile).filter(AgentProfile.id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    agent.is_active = False
    db.commit()
    return {"message": "Agent deactivated"}

# ========== 项目匹配 ==========
@router.get("/match/projects")
def match_projects(
    agent_id: Optional[int] = None,
    skills: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """智能匹配Agent技能与项目需求"""
    agent_skills = []
    if agent_id:
        agent = db.query(AgentProfile).filter(AgentProfile.id == agent_id).first()
        if agent:
            agent_skills = agent.skills or []
    if skills:
        agent_skills = skills.split(",")
    
    projects = db.query(Project).filter(Project.status == "open").all()
    
    matched = []
    for p in projects:
        tech = (p.technology_field or "").lower()
        desc = (p.description or "").lower()
        title = (p.title or "").lower()
        
        # 简单匹配算法
        score = 0
        for skill in agent_skills:
            skill_lower = skill.lower()
            if skill_lower in tech: score += 30
            if skill_lower in desc: score += 20
            if skill_lower in title: score += 15
        
        # 行业加分
        if p.industry:
            score += 10
        
        matched.append({
            "project_id": p.id,
            "title": p.title,
            "industry": p.industry,
            "budget_min": p.budget_min,
            "budget_max": p.budget_max,
            "match_score": min(100, score),
            "publisher_name": p.publisher_name,
        })
    
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    return {"matches": matched[:limit]}

# ========== Agent消息 ==========
@router.post("/messages")
def send_agent_message(
    from_agent_id: int,
    to_agent_id: Optional[int] = None,
    message_type: str = "task",
    content: str = "",
    metadata: dict = {},
    db: Session = Depends(get_db)
):
    msg = AgentMessage(
        from_agent_id=from_agent_id,
        to_agent_id=to_agent_id,
        message_type=message_type,
        content=content,
        metadata_=metadata,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "message": "Agent message sent"}

@router.get("/messages/{agent_id}")
def get_agent_messages(agent_id: int, limit: int = 20, db: Session = Depends(get_db)):
    messages = db.query(AgentMessage).filter(
        (AgentMessage.from_agent_id == agent_id) | (AgentMessage.to_agent_id == agent_id)
    ).order_by(desc(AgentMessage.created_at)).limit(limit).all()
    return {"messages": [{
        "id": m.id, "from_agent_id": m.from_agent_id, "to_agent_id": m.to_agent_id,
        "message_type": m.message_type, "content": m.content,
        "is_read": m.is_read, "created_at": m.created_at.isoformat(),
    } for m in messages]}

# ========== WebSocket A2A通信 ==========
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, agent_id: int):
        await websocket.accept()
        self.active_connections[agent_id] = websocket
    
    def disconnect(self, agent_id: int):
        self.active_connections.pop(agent_id, None)
    
    async def send_to_agent(self, agent_id: int, message: dict):
        ws = self.active_connections.get(agent_id)
        if ws:
            await ws.send_json(message)
    
    async def broadcast(self, message: dict):
        for ws in self.active_connections.values():
            await ws.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: int):
    await manager.connect(websocket, agent_id)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            # 路由消息
            target = msg.get("to_agent_id")
            if target:
                await manager.send_to_agent(target, {
                    "from_agent_id": agent_id,
                    "type": msg.get("type", "message"),
                    "content": msg.get("content", ""),
                    "timestamp": str(asyncio.get_event_loop().time()),
                })
            else:
                await manager.broadcast({
                    "from_agent_id": agent_id,
                    "type": msg.get("type", "broadcast"),
                    "content": msg.get("content", ""),
                })
    except WebSocketDisconnect:
        manager.disconnect(agent_id)

# ========== 预设Agent模板 ==========
@router.post("/seed")
def seed_agents(db: Session = Depends(get_db)):
    """创建预设Agent模板"""
    if db.query(AgentProfile).count() > 0:
        return {"message": "Agents already exist"}
    
    templates = [
        {"name": "项目猎手", "avatar_emoji": "🎯", "agent_type": "hunter",
         "description": "智能扫描揭榜挂帅平台，精准匹配技术能力与项目需求",
         "skills": ["需求分析", "技术匹配", "预算评估", "市场调研"]},
        {"name": "方案架构师", "avatar_emoji": "💡", "agent_type": "architect",
         "description": "基于项目需求生成技术方案，输出专业投标文档",
         "skills": ["方案设计", "技术选型", "文档生成", "架构评估"]},
        {"name": "商务助手", "avatar_emoji": "🤝", "agent_type": "assistant",
         "description": "管理客户关系，跟踪项目进度，协调多方沟通",
         "skills": ["客户管理", "进度跟踪", "沟通协调", "商务谈判"]},
        {"name": "数据分析师", "avatar_emoji": "📊", "agent_type": "analyst",
         "description": "分析行业趋势，评估项目价值，生成数据报告",
         "skills": ["趋势分析", "价值评估", "报告生成", "竞品分析"]},
    ]
    
    for t in templates:
        agent = AgentProfile(user_id=1, **t)
        db.add(agent)
    
    db.commit()
    return {"message": f"Created {len(templates)} agent templates"}
