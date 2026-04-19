"""
OPC Platform - 统一后端
A2A Server + Agent Engine + SecondMe + Static Frontend
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.services.agent_engine import get_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时加载匹配引擎"""
    engine = get_engine()
    print(f"🚀 OPC Platform 启动 | {len(engine.projects)}个项目 | {len(engine.all_skills)}个技能")
    yield
    print("👋 OPC Platform 关闭")


app = FastAPI(
    title="OPC Platform",
    description="一站式OPC赋能平台 - 揭榜挂帅 + 超级个体 + A2A通信",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册A2A路由
from app.api.routes.a2a import router as a2a_router
app.include_router(a2a_router, tags=["A2A超级个体"])

# 静态文件（前端页面）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs_dir = os.path.join(BASE_DIR, "docs")
if os.path.exists(docs_dir):
    app.mount("/", StaticFiles(directory=docs_dir, html=True), name="frontend")


@app.get("/api/health")
async def health():
    engine = get_engine()
    return {
        "status": "healthy",
        "platform": "OPC Platform",
        "version": "2.0.0",
        "projects": len(engine.projects),
        "skills": len(engine.all_skills),
    }
