"""
OPC Platform - SecondMe Integration
"""
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
import httpx
import json
import os
import time
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/secondme", tags=["SecondMe"])

# 正确的 SecondMe URLs
SECONDEME_API = "https://api.mindverse.com/gate/lab"
SECONDEME_OAUTH = "https://go.second-me.cn/oauth"

CLIENT_ID = os.getenv("SECONDEME_CLIENT_ID", "52754d67-3e5e-4f5e-889f-d823147927d7")
CLIENT_SECRET = os.getenv("SECONDEME_CLIENT_SECRET", "271c76f3753064447a43c5cfd0e7af5f05d842ee6b9db1b293073ec08c61f0c4")
REDIRECT_URI = os.getenv("SECONDEME_REDIRECT_URI", "https://opc-platform.onrender.com/api/secondme/callback")

_app_token_cache = {"token": None, "expires": None}


@router.get("/oauth/login")
async def oauth_login():
    """跳转 SecondMe 授权"""
    import secrets
    state = secrets.token_urlsafe(16)
    url = f"{SECONDEME_OAUTH}/?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&state={state}"
    return RedirectResponse(url=url)


@router.get("/callback")
async def oauth_callback(code: str = Query(None), state: str = Query(None), error: str = Query(None)):
    """OAuth 回调"""
    if error or not code:
        return RedirectResponse(url=f"https://opc-platform.onrender.com/superagent.html?sm_error={error or 'no_code'}")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 用授权码换 token
            resp = await client.post(
                f"{SECONDEME_API}/api/oauth/token/code",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
            )
            data = resp.json()
            
            if data.get("code") != 0:
                msg = data.get("message", "token_failed")
                return RedirectResponse(url=f"https://opc-platform.onrender.com/superagent.html?sm_error={msg}")
            
            access_token = data["data"]["accessToken"]
            
            # 获取用户信息
            user_resp = await client.get(
                f"{SECONDEME_API}/api/secondme/user/info",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_data = user_resp.json()
            user_info = user_data.get("data", {}) if user_data.get("code") == 0 else {}
            
            import urllib.parse
            profile = json.dumps({
                "name": user_info.get("name", "SecondMe用户"),
                "bio": user_info.get("bio", ""),
                "avatar": user_info.get("avatar", ""),
                "token": access_token,
            })
            encoded = urllib.parse.quote(profile)
            return RedirectResponse(
                url=f"https://opc-platform.onrender.com/superagent.html?sm_connected=true&sm_profile={encoded}"
            )
    except Exception as e:
        return RedirectResponse(url=f"https://opc-platform.onrender.com/superagent.html?sm_error=server_error")


@router.post("/connect")
async def connect_apikey(request: Request):
    """通过 API Key 连接"""
    body = await request.json()
    api_key = body.get("api_key", "")
    if not api_key.startswith("sk-"):
        raise HTTPException(400, "Invalid API Key")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{SECONDEME_API}/api/secondme/user/info",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            data = resp.json()
            if data.get("code") != 0:
                raise HTTPException(401, "Invalid")
            return {"success": True, "profile": data.get("data", {})}
    except httpx.RequestError:
        raise HTTPException(502, "Cannot reach SecondMe")


@router.post("/chat")
async def chat(request: Request):
    """与 SecondMe 对话"""
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
                f"{SECONDEME_API}/api/secondme/chat/stream",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            content = ""
            new_sid = session_id
            for line in resp.text.split("\n"):
                line = line.strip()
                if line.startswith("data: "):
                    d = line[6:]
                    if d == "[DONE]":
                        break
                    try:
                        chunk = json.loads(d)
                        if "sessionId" in chunk:
                            new_sid = chunk["sessionId"]
                        for c in chunk.get("choices", []):
                            content += c.get("delta", {}).get("content", "")
                    except:
                        pass
            return {"response": content, "session_id": new_sid}
    except Exception as e:
        raise HTTPException(502, str(e))
