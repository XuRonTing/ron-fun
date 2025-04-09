import jwt
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional, Set, Tuple, Union

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.common import ApiResponse


class AuthenticationMiddleware(BaseHTTPMiddleware):
    # 不需要认证的路径
    PUBLIC_PATHS: Set[str] = {
        "/docs", 
        "/redoc", 
        "/openapi.json",
        "/api/v1/auth/login", 
        "/api/v1/auth/register"
    }
    
    # 路径前缀匹配
    PUBLIC_PATH_PREFIXES: Tuple[str, ...] = (
        "/static/",
    )
    
    async def dispatch(
        self, request: Request, call_next
    ) -> Union[Response, JSONResponse]:
        # 检查是否需要认证
        path = request.url.path
        
        # 公开路径不需要认证
        if path in self.PUBLIC_PATHS or any(path.startswith(prefix) for prefix in self.PUBLIC_PATH_PREFIXES):
            return await call_next(request)
        
        # 验证令牌
        token = request.headers.get("Authorization")
        if not token:
            return self._create_unauthorized_response("缺少认证令牌")
        
        # 移除Bearer前缀
        if token.startswith("Bearer "):
            token = token[7:]
        
        try:
            # 解析令牌
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            if not user_id:
                return self._create_unauthorized_response("无效的认证令牌")
            
            # 验证用户是否存在
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return self._create_unauthorized_response("用户不存在")
                
                # 检查用户状态
                if not user.is_active:
                    return self._create_unauthorized_response("用户已被禁用")
                
                # 将用户信息添加到请求状态
                request.state.user = user
                request.state.user_id = user.id
                
                # 继续处理请求
                return await call_next(request)
            finally:
                db.close()
                
        except jwt.ExpiredSignatureError:
            return self._create_unauthorized_response("认证令牌已过期")
        except jwt.InvalidTokenError:
            return self._create_unauthorized_response("无效的认证令牌")
        except Exception as e:
            return self._create_unauthorized_response(f"认证失败: {str(e)}")
    
    def _create_unauthorized_response(self, message: str) -> JSONResponse:
        """创建未授权响应"""
        return JSONResponse(
            content=ApiResponse(
                code=status.HTTP_401_UNAUTHORIZED,
                message=message,
                data=None,
                timestamp=int(__import__("time").time())
            ).dict(),
            status_code=status.HTTP_401_UNAUTHORIZED
        ) 