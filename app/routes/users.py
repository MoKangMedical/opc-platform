"""
OPC Platform - 用户管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models import User
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["用户管理"])

@router.get("/me", response_model=dict, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url,
        "bio": current_user.bio,
        "role": current_user.role,
        "skills": current_user.skills or [],
        "location": current_user.location,
        "website": current_user.website,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "is_active": current_user.is_active
    }

@router.get("/{user_id}", response_model=dict, summary="获取用户信息")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "role": user.role,
        "skills": user.skills or [],
        "location": user.location,
        "website": user.website,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "is_active": user.is_active
    }

@router.get("/", response_model=List[dict], summary="获取用户列表")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（需要认证）"""
    query = db.query(User)
    
    # 过滤条件
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.display_name.contains(search) |
            User.email.contains(search)
        )
    
    users = query.offset(skip).limit(limit).all()
    
    return [{
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "skills": user.skills or [],
        "location": user.location,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "is_active": user.is_active
    } for user in users]

@router.put("/{user_id}/role", summary="更新用户角色")
async def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户角色（需要管理员权限）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    if role not in ["user", "mentor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.role = role
    db.commit()
    
    return {"message": "角色更新成功"}

@router.put("/{user_id}/status", summary="更新用户状态")
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户状态（需要管理员权限）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.is_active = is_active
    db.commit()
    
    return {"message": "状态更新成功"}

@router.get("/stats/overview", summary="用户统计")
async def user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户统计信息"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    mentors = db.query(User).filter(User.role == "mentor").count()
    admins = db.query(User).filter(User.role == "admin").count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "mentors": mentors,
        "admins": admins,
        "regular_users": total_users - mentors - admins
    }
