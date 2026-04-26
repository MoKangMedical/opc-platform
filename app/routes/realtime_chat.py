"""
OPC Platform - 实时聊天API
支持创业者实时沟通和SecondMe Agent自动介入
"""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List, Dict
import json
import asyncio
from datetime import datetime
import logging
from app.database import get_db
from app.models import (
    User, AgentProfile, ChatRoom, ChatRoomMember, ChatMessage, Message
)
from app.services.secondme_connector import get_connector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Real-time Chat"])

# ========== WebSocket连接管理 ==========
class ChatConnectionManager:
    """WebSocket连接管理器 - 支持用户和Agent连接"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # connection_id -> WebSocket
        self.user_connections: Dict[int, set] = {}  # user_id -> {connection_ids}
        self.agent_connections: Dict[int, set] = {}  # agent_id -> {connection_ids}
        self.room_connections: Dict[int, set] = {}  # room_id -> {connection_ids}
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, set] = {}
        self.agent_connections: Dict[int, set] = {}
        self.room_connections: Dict[int, set] = {}
    
    def _get_connection_id(self, user_id: int = None, agent_id: int = None) -> str:
        if user_id:
            return f"user_{user_id}_{id(asyncio)}"
        elif agent_id:
            return f"agent_{agent_id}_{id(asyncio)}"
        return f"anon_{id(asyncio)}"
    
    async def connect(self, websocket: WebSocket, user_id: int = None, agent_id: int = None):
        """建立连接"""
        await websocket.accept()
        conn_id = self._get_connection_id(user_id, agent_id)
        self.active_connections[conn_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(conn_id)
        elif agent_id:
            if agent_id not in self.agent_connections:
                self.agent_connections[agent_id] = set()
            self.agent_connections[agent_id].add(conn_id)
        
        logger.info(f"Connected: {conn_id}")
        return conn_id
    
    def disconnect(self, conn_id: str, user_id: int = None, agent_id: int = None):
        """断开连接"""
        self.active_connections.pop(conn_id, None)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(conn_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        elif agent_id and agent_id in self.agent_connections:
            self.agent_connections[agent_id].discard(conn_id)
            if not self.agent_connections[agent_id]:
                del self.agent_connections[agent_id]
        
        # 从所有房间移除
        for room_id, conns in self.room_connections.items():
            conns.discard(conn_id)
        
        logger.info(f"Disconnected: {conn_id}")
    
    async def join_room(self, conn_id: str, room_id: int):
        """加入聊天室"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        self.room_connections[room_id].add(conn_id)
    
    async def leave_room(self, conn_id: str, room_id: int):
        """离开聊天室"""
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(conn_id)
    
    async def send_to_connection(self, conn_id: str, message: dict):
        """发送消息到指定连接"""
        ws = self.active_connections.get(conn_id)
        if ws:
            try:
                await ws.send_json(message)
            except:
                self.active_connections.pop(conn_id, None)
    
    async def send_to_user(self, user_id: int, message: dict):
        """发送消息到用户的所有连接"""
        conn_ids = self.user_connections.get(user_id, set())
        for conn_id in conn_ids:
            await self.send_to_connection(conn_id, message)
    
    async def send_to_agent(self, agent_id: int, message: dict):
        """发送消息到Agent的所有连接"""
        conn_ids = self.agent_connections.get(agent_id, set())
        for conn_id in conn_ids:
            await self.send_to_connection(conn_id, message)
    
    async def broadcast_to_room(self, room_id: int, message: dict, exclude_conn: str = None):
        """向房间内所有人广播"""
        conn_ids = self.room_connections.get(room_id, set())
        for conn_id in conn_ids:
            if conn_id != exclude_conn:
                await self.send_to_connection(conn_id, message)


# 全局连接管理器
chat_manager = ChatConnectionManager()


# ========== 聊天室管理 ==========
@router.get("/rooms")
def list_chat_rooms(
    room_type: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取聊天室列表"""
    query = db.query(ChatRoom).filter(ChatRoom.is_active == True)
    
    if room_type:
        query = query.filter(ChatRoom.room_type == room_type)
    
    rooms = query.order_by(desc(ChatRoom.created_at)).all()
    
    result = []
    for room in rooms:
        # 获取成员数
        member_count = db.query(ChatRoomMember).filter(
            ChatRoomMember.room_id == room.id
        ).count()
        
        # 获取最后一条消息
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.room_id == room.id
        ).order_by(desc(ChatMessage.created_at)).first()
        
        result.append({
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "room_type": room.room_type,
            "member_count": member_count,
            "last_message": {
                "content": last_msg.content[:100] if last_msg else None,
                "sender_name": last_msg.sender_name if last_msg else None,
                "created_at": last_msg.created_at.isoformat() if last_msg else None,
            } if last_msg else None,
            "created_at": room.created_at.isoformat(),
        })
    
    return {"rooms": result}


@router.post("/rooms")
def create_chat_room(
    name: str = "",
    description: str = "",
    room_type: str = "public",
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """创建聊天室"""
    room = ChatRoom(
        name=name,
        description=description,
        room_type=room_type,
        created_by=user_id
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    
    # 创建者自动加入
    member = ChatRoomMember(
        room_id=room.id,
        user_id=user_id,
        role="owner"
    )
    db.add(member)
    db.commit()
    
    return {"id": room.id, "message": f"Chat room '{name}' created"}


@router.get("/rooms/{room_id}")
def get_chat_room(room_id: int, db: Session = Depends(get_db)):
    """获取聊天室详情"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(404, "Chat room not found")
    
    # 获取成员
    members = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id
    ).all()
    
    member_list = []
    for m in members:
        if m.user_id:
            user = db.query(User).filter(User.id == m.user_id).first()
            member_list.append({
                "type": "user",
                "id": m.user_id,
                "name": user.display_name or user.username if user else "Unknown",
                "role": m.role,
            })
        elif m.agent_id:
            agent = db.query(AgentProfile).filter(AgentProfile.id == m.agent_id).first()
            member_list.append({
                "type": "agent",
                "id": m.agent_id,
                "name": agent.name if agent else "Unknown Agent",
                "avatar_emoji": agent.avatar_emoji if agent else "🤖",
                "role": m.role,
            })
    
    return {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "room_type": room.room_type,
        "members": member_list,
        "created_at": room.created_at.isoformat(),
    }


@router.post("/rooms/{room_id}/join")
def join_chat_room(
    room_id: int,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """加入聊天室"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(404, "Chat room not found")
    
    existing = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.user_id == user_id
    ).first()
    
    if existing:
        return {"message": "Already a member"}
    
    member = ChatRoomMember(
        room_id=room_id,
        user_id=user_id,
        role="member"
    )
    db.add(member)
    db.commit()
    
    return {"message": "Joined chat room"}


@router.post("/rooms/{room_id}/invite-agent")
async def invite_agent_to_room(
    room_id: int,
    agent_id: int = None,
    secondme_route: str = None,
    db: Session = Depends(get_db)
):
    """邀请Agent加入聊天室（SecondMe集成）"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(404, "Chat room not found")
    
    if secondme_route:
        # 从SecondMe创建Agent并加入
        connector = get_connector()
        profile = await connector.get_user_profile(secondme_route)
        if not profile:
            raise HTTPException(400, "SecondMe profile not found")
        
        # 检查是否已有Agent
        agent = db.query(AgentProfile).filter(
            AgentProfile.name == f"{profile.nickname}的Agent"
        ).first()
        
        if not agent:
            agent = AgentProfile(
                user_id=1,  # 系统Agent
                user_id=1,
                name=f"{profile.nickname}的Agent",
                avatar_emoji="🧠",
                agent_type="secondme",
                description=profile.bio or f"基于SecondMe创建的数字分身",
                skills=profile.focus_areas,
                config={"secondme_route": profile.route}
            )
            db.add(agent)
            db.commit()
            db.refresh(agent)
        
        agent_id = agent.id
    
    if not agent_id:
        raise HTTPException(400, "Either agent_id or secondme_route is required")
    
    # 检查Agent是否已在房间
    existing = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.agent_id == agent_id
    ).first()
    
    if existing:
        return {"message": "Agent already in room", "agent_id": agent_id}
    
    member = ChatRoomMember(
        room_id=room_id,
        agent_id=agent_id,
        role="agent"
    )
    db.add(member)
    db.commit()
    
    return {"message": "Agent joined chat room", "agent_id": agent_id}


# ========== 聊天消息 ==========
@router.get("/rooms/{room_id}/messages")
def get_chat_messages(
    room_id: int,
    limit: int = Query(50, ge=1, le=200),
    before_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取聊天室消息历史"""
    query = db.query(ChatMessage).filter(ChatMessage.room_id == room_id)
    
    if before_id:
        query = query.filter(ChatMessage.id < before_id)
    
    messages = query.order_by(desc(ChatMessage.created_at)).limit(limit).all()
    messages.reverse()  # 按时间正序
    messages.reverse()
    
    return {"messages": [{
        "id": m.id,
        "room_id": m.room_id,
        "sender_type": m.sender_type,
        "sender_user_id": m.sender_user_id,
        "sender_agent_id": m.sender_agent_id,
        "sender_name": m.sender_name,
        "content": m.content,
        "message_type": m.message_type,
        "created_at": m.created_at.isoformat(),
    } for m in messages]}


# ========== WebSocket实时聊天 ==========
@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    user_id: int = 0,
    agent_id: int = 0
):
    """
    WebSocket实时聊天连接
    
    消息协议:
    - {type: "join", room_id: N} - 加入房间
    - {type: "leave", room_id: N} - 离开房间
    - {type: "message", room_id: N, content: "..."} - 发送消息
    - {type: "agent_chat", room_id: N, content: "...", target_secondme: "route"} - 与Agent对话
    """
    conn_id = await chat_manager.connect(websocket, user_id or None, agent_id or None)
    
    # 获取用户名
    conn_id = await chat_manager.connect(websocket, user_id or None, agent_id or None)
    
    sender_name = "Anonymous"
    if user_id:
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                sender_name = user.display_name or user.username
        finally:
            db.close()
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except:
                await chat_manager.send_to_connection(conn_id, {
                    "type": "error",
                    "content": "Invalid JSON format"
                })
                continue
            
            msg_type = msg.get("type", "message")
            room_id = msg.get("room_id")
            
            if msg_type == "join":
                # 加入聊天室
                if room_id:
                    await chat_manager.join_room(conn_id, room_id)
                    await chat_manager.send_to_connection(conn_id, {
                        "type": "system",
                        "content": f"Joined room {room_id}"
                    })
                    
                    # 广播通知
                    await chat_manager.broadcast_to_room(room_id, {
                        "type": "system",
                        "content": f"{sender_name} joined the chat",
                        "timestamp": datetime.utcnow().isoformat()
                    }, exclude_conn=conn_id)
            
            elif msg_type == "leave":
                # 离开聊天室
                if room_id:
                    await chat_manager.leave_room(conn_id, room_id)
                    await chat_manager.broadcast_to_room(room_id, {
                        "type": "system",
                        "content": f"{sender_name} left the chat",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            elif msg_type == "message":
                # 发送消息
                content = msg.get("content", "")
                if room_id and content:
                    # 保存到数据库
                content = msg.get("content", "")
                if room_id and content:
                    from app.database import SessionLocal
                    db = SessionLocal()
                    try:
                        chat_msg = ChatMessage(
                            room_id=room_id,
                            sender_type="user" if user_id else "anonymous",
                            sender_user_id=user_id or None,
                            sender_name=sender_name,
                            content=content,
                            message_type="text"
                        )
                        db.add(chat_msg)
                        db.commit()
                        db.refresh(chat_msg)
                        
                        # 广播到房间
                        broadcast_msg = {
                            "type": "message",
                            "id": chat_msg.id,
                            "room_id": room_id,
                            "sender_type": "user",
                            "sender_id": user_id,
                            "sender_name": sender_name,
                            "content": content,
                            "timestamp": chat_msg.created_at.isoformat()
                        }
                        await chat_manager.broadcast_to_room(room_id, broadcast_msg)
                    finally:
                        db.close()
            
            elif msg_type == "agent_chat":
                # 与SecondMe Agent对话
                content = msg.get("content", "")
                target_secondme = msg.get("target_secondme", "")
                
                if room_id and content and target_secondme:
                    # 保存用户消息
                    from app.database import SessionLocal
                    db = SessionLocal()
                    try:
                        # 用户消息
                    from app.database import SessionLocal
                    db = SessionLocal()
                    try:
                        user_msg = ChatMessage(
                            room_id=room_id,
                            sender_type="user",
                            sender_user_id=user_id,
                            sender_name=sender_name,
                            content=content,
                            message_type="text"
                        )
                        db.add(user_msg)
                        db.commit()
                        
                        # 广播用户消息
                        await chat_manager.broadcast_to_room(room_id, {
                            "type": "message",
                            "room_id": room_id,
                            "sender_type": "user",
                            "sender_id": user_id,
                            "sender_name": sender_name,
                            "content": content,
                            "timestamp": user_msg.created_at.isoformat()
                        })
                        
                        # 调用SecondMe
                        connector = get_connector()
                        agent_response = await connector.chat_with_secondme(target_secondme, content)
                        
                        if agent_response:
                            # 获取Agent名称
                            profile = await connector.get_user_profile(target_secondme)
                            agent_name = f"{profile.nickname}的Agent" if profile else "SecondMe Agent"
                            
                            # 保存Agent响应
                            profile = await connector.get_user_profile(target_secondme)
                            agent_name = f"{profile.nickname}的Agent" if profile else "SecondMe Agent"
                            
                            agent_msg = ChatMessage(
                                room_id=room_id,
                                sender_type="agent",
                                sender_name=agent_name,
                                content=agent_response,
                                message_type="agent_response",
                                metadata_={"secondme_route": target_secondme}
                            )
                            db.add(agent_msg)
                            db.commit()
                            db.refresh(agent_msg)
                            
                            # 广播Agent响应
                            await chat_manager.broadcast_to_room(room_id, {
                                "type": "agent_response",
                                "id": agent_msg.id,
                                "room_id": room_id,
                                "sender_type": "agent",
                                "sender_name": agent_name,
                                "content": agent_response,
                                "timestamp": agent_msg.created_at.isoformat()
                            })
                        else:
                            await chat_manager.send_to_connection(conn_id, {
                                "type": "error",
                                "content": "Agent is not responding. Please try again."
                            })
                    finally:
                        db.close()
            
            elif msg_type == "ping":
                # 心跳
                await chat_manager.send_to_connection(conn_id, {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        chat_manager.disconnect(conn_id, user_id or None, agent_id or None)


# ========== 私信系统（保留兼容） ===@router.get("/messages")
def get_messages(user_id: int = 1, db: Session = Depends(get_db)):
    """获取私信列表"""
=======
# ========== 私信系统 ==========
@router.get("/messages")
def get_messages(user_id: int = 1, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(desc(Message.created_at)).limit(50).all()
    return {"messages": [{
        "id": m.id, "sender_id": m.sender_id, "receiver_id": m.receiver_id,
        "content": m.content, "is_read": m.is_read, "created_at": m.created_at.isoformat(),
    } for m in messages]}


@router.post("/messages")
def send_message(
    sender_id: int = 1,
    receiver_id: int = 1,
    content: str = "",
    db: Session = Depends(get_db)
):
    """发送私信"""
    msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "message": "Message sent"}


# ========== 预设聊天室 ==========
@router.post("/seed-rooms")
def seed_chat_rooms(db: Session = Depends(get_db)):
    """创建预设聊天室"""
    if db.query(ChatRoom).count() > 0:
        return {"message": "Chat rooms already exist"}
    
    rooms = [
        {
            "name": "🎯 OPC创业者大厅",
            "description": "全球OPC创业者实时交流，分享经验，寻找合作伙伴",
            "room_type": "public"
        },
        {
            "name": "💡 AI+创业讨论",
            "description": "探讨AI在创业中的应用，与AI Agent实时互动",
            "room_type": "agent_hybrid"
        },
        {
            "name": "🚀 技术合伙人寻找",
            "description": "寻找技术合伙人，组建创业团队",
            "room_type": "public"
        },
        {
            "name": "💰 投融资对接",
            "description": "投资人和创业者直接对话",
            "room_type": "public"
        },
        {
            "name": "🧠 SecondMe Agent中心",
            "description": "邀请你的SecondMe数字分身加入，让Agent帮你交流",
            "room_type": "agent_hybrid"
        },
    ]
    
    for r in rooms:
        room = ChatRoom(**r)
        db.add(room)
    
    db.commit()
    return {"message": f"Created {len(rooms)} chat rooms"}
