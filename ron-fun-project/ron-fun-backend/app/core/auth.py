import functools
from datetime import datetime, timedelta
from typing import Optional, Any, Callable

from jose import jwt

from app.core.config import settings


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        subject: 令牌主体，通常是用户ID
        expires_delta: 过期时间增量
        
    Returns:
        访问令牌字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
    to_encode = {"exp": expire.timestamp(), "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def requires_auth(func: Callable) -> Callable:
    """
    认证装饰器，可用于需要认证的路由
    
    Args:
        func: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 此装饰器仅作为标记使用，实际认证在Depends(get_current_user)中完成
        return await func(*args, **kwargs)
    
    return wrapper 