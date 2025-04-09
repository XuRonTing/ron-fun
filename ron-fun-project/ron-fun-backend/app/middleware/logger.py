import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("api")

class LoggerMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件，记录请求和响应的详细信息
    """
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        
        # 记录请求信息
        logger.info(f"Request started: [ID: {request_id}] {method} {url} from {client_host}")
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            status_code = response.status_code
            logger.info(
                f"Request completed: [ID: {request_id}] {method} {url} "
                f"- Status: {status_code} - Duration: {process_time:.4f}s"
            )
            
            # 在响应头中添加请求ID和处理时间
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 处理请求过程中发生的异常
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: [ID: {request_id}] {method} {url} "
                f"- Error: {str(e)} - Duration: {process_time:.4f}s"
            )
            raise  # 重新抛出异常，让后续的异常处理中间件处理 