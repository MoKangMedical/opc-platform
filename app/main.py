"""
OPC Platform - 统一后端
A2A Server + Agent Engine + Static Frontend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="OPC Platform",
    description="一站式OPC赋能平台 - 揭榜挂帅 + 超级个体 + A2A通信",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册A2A路由
try:
    from app.api.routes.a2a import router as a2a_router
    app.include_router(a2a_router, tags=["A2A超级个体"])
    print("✅ A2A router loaded")
except Exception as e:
    print(f"⚠️ A2A router error: {e}")

# 静态文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs_dir = os.path.join(BASE_DIR, "docs")
if os.path.exists(docs_dir):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=docs_dir, html=True), name="frontend")
    print(f"✅ Static files: {docs_dir}")
else:
    print(f"⚠️ Docs dir not found: {docs_dir}")


@app.get("/api/health")
async def health():
    try:
        from app.services.agent_engine import get_engine
        engine = get_engine()
        return {
            "status": "healthy",
            "platform": "OPC Platform",
            "projects": len(engine.projects),
            "skills": len(engine.all_skills),
        }
    except Exception as e:
        return {"status": "healthy", "platform": "OPC Platform", "error": str(e)}
