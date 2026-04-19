"""
OPC Platform - SecondMe Integration
连接 SecondMe 数字分身到 OPC Agent
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import httpx
import json
import os
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/secondme", tags=["SecondMe"])

SECONDBASE = "https://api.mindverse.com/gate/lab"

# 应用凭证 (从 SecondMe Developer Console 获取)
CLIENT_ID = os.getenv("SECONDEME_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SECONDEME_CLIENT_SECRET", "")

# 缓存应用 token
_app_token_cache = {"token": None, "expires": None}

async def get_app_token() -> str:
    """获取应用级 token (client_credentials)"""
    global _app_token_cache
    if _app_token_cache["token"] and _app_token_cache["expires"] and datetime.now() < _app_token_cache["expires"]:
        return _app_token_cache["token"]
    
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(500, "SecondMe credentials not configured")
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SECONDBASE}/api/oauth/token/client",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "chat.write",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = resp.json()
        if data.get("code") != 0:
            raise HTTPException(500, f"SecondMe auth failed: {data.get('message')}")
        
        token = data["data"]["accessToken"]
        expires_in = data["data"].get("expiresIn", 604800)
        _app_token_cache = {
            "token": token,
            "expires": datetime.now() + timedelta(seconds=expires_in - 300),
        }
        return token


@router.post("/connect")
async def connect_secondme(request: Request):
    """用户通过 API Key 连接 SecondMe"""
    body = await request.json()
    api_key = body.get("api_key", "")
    agent_id = body.get("agent_id", "")
    
    if not api_key or not api_key.startswith("sk-"):
        raise HTTPException(400, "Invalid SecondMe API Key (must start with sk-)")
    
    # 验证 API Key 有效性 - 获取用户信息
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{SECONDBASE}/api/secondme/user/info",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            data = resp.json()
            if data.get("code") != 0:
                raise HTTPException(401, "Invalid API Key")
            
            user_info = data.get("data", {})
            return {
                "success": True,
                "message": "SecondMe 连接成功",
                "profile": {
                    "name": user_info.get("name", "Unknown"),
                    "bio": user_info.get("bio", ""),
                    "avatar": user_info.get("avatar", ""),
                },
                "agent_id": agent_id,
            }
    except httpx.RequestError:
        raise HTTPException(502, "Cannot reach SecondMe API")


@router.post("/chat")
async def chat_with_secondme(request: Request):
    """与 SecondMe 数字分身对话"""
    body = await request.json()
    api_key = body.get("api_key", "")
    message = body.get("message", "")
    session_id = body.get("session_id")
    
    if not api_key:
        raise HTTPException(400, "API key required")
    if not message:
        raise HTTPException(400, "Message required")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"message": message}
            if session_id:
                payload["sessionId"] = session_id
            
            resp = await client.post(
                f"{SECONDBASE}/api/secondme/chat/stream",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            
            # 解析 SSE 流
            content = ""
            new_session_id = session_id
            for line in resp.text.split("
"):
                line = line.strip()
                if line.startswith("event: session"):
                    continue
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if "sessionId" in chunk:
                            new_session_id = chunk["sessionId"]
                        if "choices" in chunk:
                            for choice in chunk["choices"]:
                                delta = choice.get("delta", {})
                                if "content" in delta:
                                    content += delta["content"]
                    except json.JSONDecodeError:
                        pass
            
            return {
                "response": content,
                "session_id": new_session_id,
            }
    except httpx.RequestError as e:
        raise HTTPException(502, f"SecondMe API error: {str(e)}")


@router.post("/visitor-chat/init")
async def init_visitor_chat(request: Request):
    """初始化访客对话 (匿名模式)"""
    body = await request.json()
    api_key = body.get("api_key", "")
    visitor_name = body.get("visitor_name", "OPC访客")
    
    if not api_key:
        raise HTTPException(400, "SecondMe API key required")
    
    try:
        app_token = await get_app_token()
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{SECONDBASE}/api/secondme/visitor-chat/init",
                headers={
                    "Authorization": f"Bearer {app_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "apiKey": api_key,
                    "visitorId": f"opc_{datetime.now().timestamp()}",
                    "visitorName": visitor_name,
                },
            )
            data = resp.json()
            if data.get("code") != 0:
                return {"success": False, "error": data.get("message", "Init failed")}
            
            return {
                "success": True,
                "session_id": data["data"].get("sessionId"),
                "ws_url": data["data"].get("wsUrl"),
            }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/visitor-chat/send")
async def send_visitor_message(request: Request):
    """发送访客消息"""
    body = await request.json()
    api_key = body.get("api_key", "")
    session_id = body.get("session_id", "")
    message = body.get("message", "")
    
    if not all([api_key, session_id, message]):
        raise HTTPException(400, "Missing required fields")
    
    try:
        app_token = await get_app_token()
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{SECONDBASE}/api/secondme/visitor-chat/send",
                headers={
                    "Authorization": f"Bearer {app_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "apiKey": api_key,
                    "sessionId": session_id,
                    "message": message,
                },
            )
            data = resp.json()
            return {"success": data.get("code") == 0, "data": data}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/chat/agents")
def list_secondme_agents():
    """列出可用的 SecondMe 集成"""
    return {
        "agents": [
            {
                "id": "secondme",
                "name": "SecondMe 数字分身",
                "emoji": "🧠",
                "description": "连接你的 SecondMe AI 分身，让你的 Agent 拥有你的个性和记忆",
                "connect_url": "/api/secondme/connect",
                "chat_url": "/api/secondme/chat",
            }
        ],
        "setup_guide": {
            "step1": "访问 app.mindos.com 创建你的 SecondMe",
            "step2": "在 SecondMe 设置中获取 API Key (sk- 开头)",
            "step3": "在 OPC 平台输入 API Key 连接",
        },
    }
