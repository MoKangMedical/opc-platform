"""
OPC SuperAgent - A2A Server
Agent-to-Agent 通信服务，基于WebSocket + JSON-RPC 2.0
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """A2A 消息类型"""
    DISCOVER = "discover"           # Agent发现
    GREETING = "greeting"           # 问候
    CAPABILITY_QUERY = "capability_query"   # 能力查询
    CAPABILITY_MATCH = "capability_match"   # 能力匹配
    TASK_PROPOSAL = "task_proposal"         # 任务提议
    TASK_ACCEPT = "task_accept"             # 任务接受
    TASK_REJECT = "task_reject"             # 任务拒绝
    COLLABORATION = "collaboration"         # 协作讨论
    USER_MESSAGE = "user_message"           # 用户消息
    AGENT_RESPONSE = "agent_response"       # Agent回复
    HEARTBEAT = "heartbeat"                 # 心跳


@dataclass
class AgentCard:
    """Agent 能力卡片 (A2A Agent Card)"""
    agent_id: str
    name: str
    owner_name: str
    avatar: str = "🤖"
    role: str = ""
    organization: str = ""
    skills: List[str] = field(default_factory=list)
    bio: str = ""
    secondme_route: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    status: str = "online"  # online, busy, offline
    projects_matched: int = 0
    conversations: int = 0
    match_accuracy: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentCard":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class A2AMessage:
    """A2A 消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    sender_id: str = ""
    receiver_id: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_jsonrpc(self) -> dict:
        """转换为 JSON-RPC 2.0 格式"""
        return {
            "jsonrpc": "2.0",
            "method": self.type,
            "params": {
                "message_id": self.id,
                "sender": self.sender_id,
                "receiver": self.receiver_id,
                "content": self.content,
                "metadata": self.metadata,
            },
            "id": self.id,
        }

    @classmethod
    def from_jsonrpc(cls, data: dict) -> "A2AMessage":
        params = data.get("params", {})
        return cls(
            id=params.get("message_id", str(uuid.uuid4())),
            type=data.get("method", ""),
            sender_id=params.get("sender", ""),
            receiver_id=params.get("receiver", ""),
            content=params.get("content", ""),
            metadata=params.get("metadata", {}),
        )


class A2AServer:
    """A2A 通信服务器"""

    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}
        self.connections: Dict[str, Any] = {}  # agent_id -> websocket
        self.message_history: List[A2AMessage] = []
        self.rooms: Dict[str, List[str]] = {}  # room_id -> [agent_ids]

    def register_agent(self, card: AgentCard) -> str:
        """注册Agent"""
        self.agents[card.agent_id] = card
        logger.info(f"Agent registered: {card.name} ({card.agent_id})")
        return card.agent_id

    def unregister_agent(self, agent_id: str):
        """注销Agent"""
        if agent_id in self.agents:
            self.agents[agent_id].status = "offline"
        if agent_id in self.connections:
            del self.connections[agent_id]
        logger.info(f"Agent unregistered: {agent_id}")

    def get_online_agents(self) -> List[dict]:
        """获取在线Agent列表"""
        return [
            a.to_dict() for a in self.agents.values()
            if a.status != "offline"
        ]

    def find_matching_agents(self, skills: List[str], min_score: float = 0.3) -> List[dict]:
        """根据技能匹配Agent"""
        results = []
        for agent in self.agents.values():
            if agent.status == "offline":
                continue
            agent_skills = set(s.lower() for s in agent.skills)
            query_skills = set(s.lower() for s in skills)
            if not agent_skills or not query_skills:
                continue
            overlap = len(agent_skills & query_skills)
            score = overlap / max(len(agent_skills | query_skills), 1)
            if score >= min_score:
                results.append({**agent.to_dict(), "match_score": round(score, 2)})
        return sorted(results, key=lambda x: x["match_score"], reverse=True)

    async def send_message(self, message: A2AMessage) -> bool:
        """发送A2A消息"""
        self.message_history.append(message)
        receiver_ws = self.connections.get(message.receiver_id)
        if receiver_ws:
            try:
                await receiver_ws.send_json(message.to_jsonrpc())
                return True
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
        return False

    async def broadcast(self, message: A2AMessage, exclude: str = None):
        """广播消息"""
        for agent_id, ws in self.connections.items():
            if agent_id == exclude:
                continue
            try:
                await ws.send_json(message.to_jsonrpc())
            except Exception:
                pass

    async def handle_connection(self, websocket, agent_id: str):
        """处理WebSocket连接"""
        self.connections[agent_id] = websocket
        if agent_id in self.agents:
            self.agents[agent_id].status = "online"

        # 广播新Agent上线
        online_msg = A2AMessage(
            type=MessageType.DISCOVER,
            sender_id=agent_id,
            content=f"Agent {agent_id} is now online",
            metadata={"agents": self.get_online_agents()},
        )
        await self.broadcast(online_msg, exclude=agent_id)

        try:
            async for raw in websocket:
                try:
                    data = json.loads(raw)
                    msg = A2AMessage.from_jsonrpc(data)
                    msg.sender_id = agent_id
                    await self._dispatch_message(msg, websocket)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {agent_id}")
        except Exception as e:
            logger.info(f"Connection closed: {agent_id} - {e}")
        finally:
            self.unregister_agent(agent_id)

    async def _dispatch_message(self, msg: A2AMessage, sender_ws):
        """消息分发"""
        if msg.type == MessageType.HEARTBEAT:
            await sender_ws.send_json({"jsonrpc": "2.0", "result": "pong", "id": msg.id})
            return

        if msg.receiver_id:
            # 点对点消息
            sent = await self.send_message(msg)
            if not sent:
                # Agent不在线，缓存消息
                logger.info(f"Agent {msg.receiver_id} offline, message queued")
        else:
            # 广播
            await self.broadcast(msg, exclude=msg.sender_id)

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_agents": len(self.agents),
            "online_agents": sum(1 for a in self.agents.values() if a.status == "online"),
            "total_messages": len(self.message_history),
            "active_connections": len(self.connections),
        }


# 全局单例
a2a_server = A2AServer()
