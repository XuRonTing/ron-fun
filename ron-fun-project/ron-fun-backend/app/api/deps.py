from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.auth import requires_auth
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.exp < datetime.timestamp(datetime.now()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(User).filter(User.id == token_data.sub).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    return user

@requires_auth
async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃的超级管理员用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="普通用户没有访问权限"
        )
    return current_user

async def get_optional_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme_optional)
) -> Optional[User]:
    """
    获取可选的当前用户
    
    与get_current_user的区别是，如果没有提供token或token无效，不会抛出异常，而是返回None
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.exp < datetime.timestamp(datetime.now()):
            return None
    except (JWTError, ValidationError):
        return None
        
    user = db.query(User).filter(User.id == token_data.sub).first()
    
    if not user or not user.is_active:
        return None
        
    return user