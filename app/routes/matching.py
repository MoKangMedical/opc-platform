"""
OPC Platform - 匹配算法API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User
from app.routes.auth import get_current_user
from app.services.matching import MatchingService

router = APIRouter(prefix="/api/matching", tags=["匹配算法"])

@router.get("/projects/{project_id}/users", summary="为项目匹配用户")
async def match_users_to_project(
    project_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为指定项目匹配合适的用户"""
    matching_service = MatchingService(db)
    matches = matching_service.match_users_to_project(project_id, limit)
    
    return {
        "project_id": project_id,
        "matches": matches,
        "total": len(matches)
    }

@router.get("/users/{user_id}/projects", summary="为用户匹配项目")
async def match_projects_to_user(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为指定用户匹配合适的项目"""
    # 只允许用户查看自己的匹配结果
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    matching_service = MatchingService(db)
    matches = matching_service.match_projects_to_user(user_id, limit)
    
    return {
        "user_id": user_id,
        "matches": matches,
        "total": len(matches)
    }

@router.get("/users/me/recommended-projects", summary="获取推荐项目")
async def get_recommended_projects(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户推荐的项目"""
    matching_service = MatchingService(db)
    matches = matching_service.match_projects_to_user(current_user.id, limit)
    
    return {
        "user_id": current_user.id,
        "matches": matches,
        "total": len(matches)
    }

@router.get("/users/me/recommended-mentors", summary="获取推荐导师")
async def get_recommended_mentors(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户推荐的导师"""
    matching_service = MatchingService(db)
    matches = matching_service.get_mentor_matches(current_user.id, limit)
    
    return {
        "user_id": current_user.id,
        "matches": matches,
        "total": len(matches)
    }

@router.get("/stats", summary="获取匹配统计")
async def get_matching_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取匹配统计信息"""
    matching_service = MatchingService(db)
    stats = matching_service.get_matching_stats()
    
    return stats

@router.get("/users/me/match-score/{project_id}", summary="获取匹配分数")
async def get_match_score(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户与指定项目的匹配分数"""
    matching_service = MatchingService(db)
    
    # 获取项目
    from app.models import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 提取项目关键词
    project_keywords = matching_service.extract_keywords_from_project(project)
    
    # 计算匹配分数
    if not current_user.skills:
        match_score = 0
        match_reasons = []
    else:
        match_score = matching_service.calculate_skill_match_score(
            current_user.skills, project_keywords
        )
        match_reasons = matching_service._get_match_reasons(
            current_user.skills, project_keywords
        )
    
    return {
        "user_id": current_user.id,
        "project_id": project_id,
        "match_score": match_score,
        "match_reasons": match_reasons,
        "user_skills": current_user.skills or [],
        "project_keywords": project_keywords
    }
