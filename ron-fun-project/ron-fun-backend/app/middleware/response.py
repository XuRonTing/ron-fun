import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any, Dict, Optional, Union

from app.schemas.common import ApiResponse


class ResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next
    ) -> Union[Response, JSONResponse]:
        try:
            response = await call_next(request)
            
            # 如果是API路由并且是JSON响应，则统一包装格式
            if (
                request.url.path.startswith("/api/")
                and response.status_code < 500
                and response.headers.get("content-type") == "application/json"
            ):
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                # 解析响应体
                body = response_body.decode()
                import json
                data = json.loads(body)
                
                # 构造统一响应格式
                wrapped_response = ApiResponse(
                    code=0 if 200 <= response.status_code < 400 else response.status_code,
                    message="success" if 200 <= response.status_code < 400 else data.get("detail", "error"),
                    data=data if 200 <= response.status_code < 400 else None,
                    timestamp=int(time.time())
                )
                
                return JSONResponse(
                    content=wrapped_response.dict(),
                    status_code=200 if 200 <= response.status_code < 400 else response.status_code,
                    headers=dict(response.headers)
                )
            
            return response
            
        except Exception as e:
            # 异常处理
            wrapped_response = ApiResponse(
                code=500,
                message=str(e),
                data=None,
                timestamp=int(time.time())
            )
            
            return JSONResponse(
                content=wrapped_response.dict(),
                status_code=500
            ) 