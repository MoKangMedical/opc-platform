"""
OPC Platform - 认证中间件
"""
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.routes.auth import get_current_user

def require_auth(func):
    """需要认证的装饰器"""
    @wraps(func)
    async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper

def require_role(allowed_roles: list):
    """需要特定角色的装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_admin(func):
    """需要管理员权限的装饰器"""
    return require_role(["admin"])(func)

def require_mentor(func):
    """需要导师权限的装饰器"""
    return require_role(["mentor", "admin"])(func)

def optional_auth(func):
    """可选认证的装饰器（认证后提供更多信息，但不强制）"""
    @wraps(func)
    async def wrapper(*args, db: Session = Depends(get_db), **kwargs):
        # 尝试获取当前用户
        try:
            current_user = await get_current_user(db=db, **kwargs)
        except HTTPException:
            current_user = None
        
        return await func(*args, current_user=current_user, db=db, **kwargs)
    return wrapper
