import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.response import ApiResponse

# 配置日志
logger = logging.getLogger("exception")

class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    异常处理中间件，集中处理应用程序中的异常
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ValidationError as e:
            # 处理Pydantic验证错误
            logger.warning(f"ValidationError: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=ApiResponse(
                    code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    message="数据验证错误",
                    data=e.errors()
                ).dict()
            )
        except SQLAlchemyError as e:
            # 处理数据库错误
            logger.error(f"DatabaseError: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ApiResponse(
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="数据库操作错误",
                    data=None
                ).dict()
            )
        except Exception as e:
            # 处理其他未预期的异常
            error_detail = str(e)
            stack_trace = traceback.format_exc()
            
            # 记录错误详情和堆栈跟踪
            logger.error(f"Unhandled Exception: {error_detail}\n{stack_trace}")
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ApiResponse(
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="服务器内部错误",
                    data=None
                ).dict()
            ) 