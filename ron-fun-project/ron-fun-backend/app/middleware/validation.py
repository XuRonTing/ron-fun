from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Callable, Optional, Type
from pydantic import BaseModel, ValidationError
import logging
import json

from app.schemas.response import ApiResponse

# 配置日志
logger = logging.getLogger("validation")

class ValidationMiddleware(BaseHTTPMiddleware):
    """
    参数验证中间件，提供集中的请求参数验证
    """
    
    def __init__(self, app, validators: Dict[str, Type[BaseModel]] = None):
        """
        初始化验证中间件
        
        Args:
            app: FastAPI应用实例
            validators: 路径对应的验证模型字典，格式为 {"/api/v1/path": ModelClass}
        """
        super().__init__(app)
        self.validators = validators or {}
    
    async def dispatch(self, request: Request, call_next):
        # 获取当前请求路径
        path = request.url.path
        
        # 检查是否需要验证该路径的请求
        validator = self._get_validator(path)
        
        if validator and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 获取请求体数据
                body = await request.body()
                if body:
                    # 解析JSON数据
                    try:
                        body_data = json.loads(body)
                    except json.JSONDecodeError:
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content=ApiResponse(
                                code=status.HTTP_400_BAD_REQUEST,
                                message="无效的JSON格式",
                                data=None
                            ).dict()
                        )
                    
                    # 使用Pydantic模型验证数据
                    try:
                        validated_data = validator(**body_data)
                        # 将验证后的数据重新附加到请求对象
                        request.state.validated_data = validated_data
                    except ValidationError as e:
                        return JSONResponse(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=ApiResponse(
                                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                message="参数验证失败",
                                data=e.errors()
                            ).dict()
                        )
            
            except Exception as e:
                logger.error(f"Validation middleware error: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ApiResponse(
                        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message="参数验证过程中发生错误",
                        data=None
                    ).dict()
                )
        
        # 继续处理请求
        return await call_next(request)
    
    def _get_validator(self, path: str) -> Optional[Type[BaseModel]]:
        """
        根据路径获取对应的验证模型
        
        Args:
            path: 请求路径
            
        Returns:
            验证模型类或None
        """
        return self.validators.get(path)
    
    def register_validator(self, path: str, validator: Type[BaseModel]):
        """
        注册路径对应的验证模型
        
        Args:
            path: API路径
            validator: Pydantic验证模型类
        """
        self.validators[path] = validator 