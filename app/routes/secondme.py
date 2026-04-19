"""
OPC Platform - SecondMe Integration
OAuth2自动登录 + 数字分身对话
"""
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
import json
import os
import time
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/secondme", tags=["SecondMe"])

SECONDBASE = "https://api.mindverse.com/gate/lab"
SECONDEME_AUTH = "https://app.mindos.com/gate/lab"

# OAuth2 配置 - 从 SecondMe Developer Console 获取
CLIENT_ID = os.getenv("SECONDEME_CLIENT_ID", "52754d67-3e5e-4f5e-889f-d823147927d7")
CLIENT_SECRET = os.getenv("SECONDEME_CLIENT_SECRET", "271c76f3753064447a43c5cfd0e7af5f05d842ee6b9db1b293073ec08c61f0c4")
REDIRECT_URI = os.getenv("SECONDEME_REDIRECT_URI", "https://opc-platform.onrender.com/api/secondme/callback")

# 应用 token 缓存
_app_token_cache = {"token": None, "expires": None}

# 用户 token 存储 (生产环境应用数据库)
_user_tokens = {}


async def get_app_token() -> str:
    """获取应用级 token (client_credentials)"""
    global _app_token_cache
    if _app_token_cache["token"] and _app_token_cache["expires"] and datetime.now() < _app_token_cache["expires"]:
        return _app_token_cache["token"]
    
    if not CLIENT_SECRET:
        raise HTTPException(500, "SecondMe client_secret not configured")
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SECONDBASE}/api/oauth/token/client",
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": "chat.write userinfo",
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


# ========== OAuth2 自动登录 ==========

@router.get("/oauth/authorize")
async def oauth_authorize(state: str = "opc_platform"):
    """Step 1: 跳转到 SecondMe 授权页面"""
    auth_url = (
        f"{SECONDEME_AUTH}/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=userinfo chat.write chat.read"
        f"&state={state}"
    )
    return {"auth_url": auth_url}


@router.get("/oauth/login")
async def oauth_login():
    """直接跳转到 SecondMe 授权 (浏览器重定向)"""
    auth_url = (
        f"{SECONDEME_AUTH}/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=userinfo chat.write chat.read"
        f"&state=opc_auto_login"
    )
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def oauth_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
):
    """Step 2: 处理 SecondMe 回调，换取 token"""
    if error:
        return RedirectResponse(url=f"https://opc-platform.onrender.com/superagent.html?sm_error={error}")
    
    if not code:
        return RedirectResponse(url="https://opc-platform.onrender.com/superagent.html?sm_error=no_code")
    
    try:
        # 用授权码换取 access token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{SECONDBASE}/api/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            data = resp.json()
            
            if data.get("code") != 0:
                return RedirectResponse(
                    url=f"https://opc-platform.onrender.com/superagent.html?sm_error=token_failed"
                )
            
            access_token = data["data"]["accessToken"]
            
            # 获取用户信息
            user_resp = await client.get(
                f"{SECONDBASE}/api/secondme/user/info",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_data = user_resp.json()
            user_info = user_data.get("data", {}) if user_data.get("code") == 0 else {}
            
            # 存储 token (用简单方式，生产环境应用数据库)
            user_id = f"sm_{int(time.time())}"
            _user_tokens[user_id] = {
                "access_token": access_token,
                "user_info": user_info,
                "created_at": datetime.now().isoformat(),
            }
            
            # 重定向回前端，带上 token 和用户信息
            profile_json = json.dumps({
                "name": user_info.get("name", "SecondMe用户"),
                "bio": user_info.get("bio", ""),
                "avatar": user_info.get("avatar", ""),
                "token": access_token,
                "user_id": user_id,
            })
            
            # URL encode the profile
            import urllib.parse
            encoded = urllib.parse.quote(profile_json)
            
            return RedirectResponse(
                url=f"https://opc-platform.onrender.com/superagent.html?sm_connected=true&sm_profile={encoded}"
            )
            
    except Exception as e:
        return RedirectResponse(
            url=f"https://opc-platform.onrender.com/superagent.html?sm_error=server_error"
        )


@router.post("/auto-connect")
async def auto_connect(request: Request):
    """前端自动连接 - 返回授权URL"""
    auth_url = (
        f"{SECONDEME_AUTH}/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=userinfo chat.write chat.read"
        f"&state=opc_auto"
    )
    return {"auth_url": auth_url, "message": "请在弹窗中完成 SecondMe 授权"}


# ========== 原有 API ==========

@router.post("/connect")
async def connect_secondme(request: Request):
    """通过 API Key 连接"""
    body = await request.json()
    api_key = body.get("api_key", "")
    
    if not api_key or not api_key.startswith("sk-"):
        raise HTTPException(400, "Invalid API Key")
    
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
                "profile": {
                    "name": user_info.get("name", "Unknown"),
                    "bio": user_info.get("bio", ""),
                    "avatar": user_info.get("avatar", ""),
                },
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
    
    if not api_key or not message:
        raise HTTPException(400, "api_key and message required")
    
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
            
            content = ""
            new_session_id = session_id
            for line in resp.text.split("\n"):
                line = line.strip()
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
            
            return {"response": content, "session_id": new_session_id}
    except httpx.RequestError as e:
        raise HTTPException(502, f"SecondMe API error: {str(e)}")


@router.get("/chat/agents")
def list_secondme_agents():
    return {
        "agents": [{
            "id": "secondme",
            "name": "SecondMe 数字分身",
            "emoji": "🧠",
            "description": "连接你的 SecondMe AI 分身",
            "oauth_login": "/api/secondme/oauth/login",
        }],
        "setup": "点击连接按钮，自动跳转 SecondMe 授权",
    }
