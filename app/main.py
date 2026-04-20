"""
OPC Platform - 统一后端服务
6大模块: 揭榜挂帅 + 超级个体 + 名人堂 + 学院 + 健康 + 社区
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import init_db, engine, Base
from app.models import *  # Import all models

app = FastAPI(
    title="OPC Platform API",
    description="一站式OPC赋能平台 - 连接OPC与需求方、OPC交流、Agent协作",
    version="3.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.routes.academy import router as academy_router
from app.routes.health import router as health_router
from app.routes.projects import router as projects_router
from app.routes.community import router as community_router
from app.routes.agents import router as agents_router
from app.routes.chat import router as chat_router
from app.routes.secondme import router as secondme_router
from app.routes.realtime_chat import router as realtime_chat_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.matching import router as matching_router
from app.routes.payment import router as payment_router

app.include_router(academy_router)
app.include_router(health_router)
app.include_router(projects_router)
app.include_router(community_router)
app.include_router(agents_router)
app.include_router(chat_router)
app.include_router(secondme_router)
app.include_router(realtime_chat_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(matching_router)
app.include_router(payment_router)

# 健康检查
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "platform": "OPC Platform", "version": "3.0.0"}

# 统计概览
@app.get("/api/stats")
async def platform_stats():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        from app.models import Project, Course, User, Mentor, HealthRecord, CommunityPost, AgentProfile
        stats = {
            "projects": db.query(Project).filter(Project.status == "open").count(),
            "courses": db.query(Course).filter(Course.is_published == True).count(),
            "users": db.query(User).count(),
            "mentors": db.query(Mentor).filter(Mentor.is_available == True).count(),
            "health_records": db.query(HealthRecord).count(),
            "community_posts": db.query(CommunityPost).count(),
            "agents": db.query(AgentProfile).filter(AgentProfile.is_active == True).count(),
        }
        return stats
    finally:
        db.close()

# 初始化数据库
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
    
    # 自动seed数据
    from app.database import SessionLocal
    from app.models import Project
    db = SessionLocal()
    try:
        if db.query(Project).count() == 0:
            print("📦 Seeding initial data...")
            # Seed projects from JSON
            import json
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jiangsu_ai_scenarios.json")
            if os.path.exists(data_path):
                with open(data_path) as f:
                    projects = json.load(f)
                for p in projects:
                    proj = Project(
                        title=p.get("title", ""),
                        project_code=p.get("project_code", ""),
                        publisher_name=p.get("publisher_name", ""),
                        contact_person=p.get("contact_person", ""),
                        contact_phone=p.get("contact_phone", ""),
                        industry=p.get("industry", ""),
                        technology_field=p.get("technology_field", ""),
                        budget_min=p.get("budget_min", 0),
                        budget_max=p.get("budget_max", 0),
                        description=p.get("description", ""),
                        status="open",
                    )
                    db.add(proj)
                db.commit()
                print(f"✅ Seeded {len(projects)} projects")
    except Exception as e:
        print(f"⚠️ Seed error: {e}")
    finally:
        db.close()

# 静态文件 (前端)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs_dir = os.path.join(BASE_DIR, "docs")
if os.path.exists(docs_dir):
    app.mount("/", StaticFiles(directory=docs_dir, html=True), name="frontend")
    print(f"✅ Static files: {docs_dir}")
