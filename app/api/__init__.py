"""
OPC Marketplace - API路由
"""

from fastapi import APIRouter

from app.api.routes import auth, users, projects, skills, matches, reviews, government

api_router = APIRouter()

# 包含各个路由模块
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目管理"])
api_router.include_router(skills.router, prefix="/skills", tags=["技能管理"])
api_router.include_router(matches.router, prefix="/matches", tags=["匹配管理"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["评价管理"])
api_router.include_router(government.router, prefix="/government", tags=["揭榜挂帅"])