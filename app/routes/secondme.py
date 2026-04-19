"""
OPC Platform - SecondMe OAuth2 Callback
处理SecondMe授权回调
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import json
import httpx

router = APIRouter(prefix="/api/secondme", tags=["SecondMe"])

# SecondMe OAuth2配置
SECONDME_CLIENT_ID = os.getenv("SECONDME_CLIENT_ID", "52754d67")
SECONDME_CLIENT_SECRET = os.getenv("SECONDME_CLIENT_SECRET", "271c76f")
SECONDME_AUTH_URL = "https://app.mindos.com/oauth/authorize"
SECONDME_TOKEN_URL = "https://app.mindos.com/oauth/token"
SECONDME_API_URL = "https://app.mindos.com/gate/lab"

@router.get("/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """SecondMe OAuth2回调处理"""
    if error:
        return HTMLResponse(f"""
        <html>
        <head><title>授权失败</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>❌ 授权失败</h1>
            <p>错误信息: {error}</p>
            <a href="/">返回首页</a>
        </body>
        </html>
        """)
    
    if not code:
        raise HTTPException(400, "Missing authorization code")
    
    # 交换access token
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(SECONDME_TOKEN_URL, data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": SECONDME_CLIENT_ID,
                "client_secret": SECONDME_CLIENT_SECRET,
                "redirect_uri": "https://opc-platform.onrender.com/api/secondme/callback"
            })
            
            if resp.status_code == 200:
                token_data = resp.json()
                access_token = token_data.get("access_token")
                
                # 获取用户信息
                user_resp = await client.get(
                    f"{SECONDME_API_URL}/user/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if user_resp.status_code == 200:
                    user_data = user_resp.json()
                    return HTMLResponse(f"""
                    <html>
                    <head>
                        <title>授权成功</title>
                        <style>
                            body {{ font-family: sans-serif; text-align: center; padding: 50px; background: #0a0a0f; color: #e4e4ef; }}
                            .card {{ background: #111118; border-radius: 12px; padding: 30px; max-width: 400px; margin: 0 auto; }}
                            .success {{ color: #00d68f; }}
                            a {{ color: #6c5ce7; }}
                        </style>
                    </head>
                    <body>
                        <div class="card">
                            <h1 class="success">✅ 授权成功</h1>
                            <p>欢迎, {user_data.get('nickname', '用户')}!</p>
                            <p>您的SecondMe数字分身已连接到OPC平台</p>
                            <script>
                                // 将token保存到localStorage
                                localStorage.setItem('secondme_token', '{access_token}');
                                localStorage.setItem('secondme_user', JSON.stringify({json.dumps(user_data)}));
                                // 3秒后跳转
                                setTimeout(() => window.location.href = '/superagent.html', 3000);
                            </script>
                            <a href="/superagent.html">立即体验 →</a>
                        </div>
                    </body>
                    </html>
                    """)
            
            return HTMLResponse("""
            <html>
            <head><title>授权失败</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>❌ 获取用户信息失败</h1>
                <a href="/">返回首页</a>
            </body>
            </html>
            """)
            
    except Exception as e:
        return HTMLResponse(f"""
        <html>
        <head><title>授权错误</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>❌ 授权过程出错</h1>
            <p>{str(e)}</p>
            <a href="/">返回首页</a>
        </body>
        </html>
        """)


@router.get("/authorize")
async def authorize():
    """生成SecondMe授权链接"""
    import urllib.parse
    params = {
        "client_id": SECONDME_CLIENT_ID,
        "redirect_uri": "https://opc-platform.onrender.com/api/secondme/callback",
        "response_type": "code",
        "scope": "user:read chat:write",
        "state": "opc_platform"
    }
    auth_url = f"{SECONDME_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return {"auth_url": auth_url}


@router.get("/status")
async def check_status():
    """检查SecondMe连接状态"""
    return {
        "client_id": SECONDME_CLIENT_ID,
        "callback_url": "https://opc-platform.onrender.com/api/secondme/callback",
        "status": "ready"
    }
