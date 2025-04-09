from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.application import Application
from app.models.user import User
from app.models.product import Product

router = APIRouter()


@router.get("/")
async def health_check(request: Request, db: AsyncSession = Depends(get_db)):
    """
    健康检查端点，返回应用程序状态和基本统计信息
    """
    # 检查数据库连接
    db_status = True
    stats = {}
    
    try:
        # 获取基本统计数据
        user_count = await db.execute(User.count())
        stats["user_count"] = user_count.scalar() or 0
        
        product_count = await db.execute(Product.count())
        stats["product_count"] = product_count.scalar() or 0
        
        app_count = await db.execute(Application.count())
        stats["application_count"] = app_count.scalar() or 0
        
    except Exception as e:
        db_status = False
        stats["error"] = str(e)
    
    # 构建响应
    return {
        "status": "healthy" if db_status else "unhealthy",
        "version": "1.0.0",
        "db_connection": "ok" if db_status else "failed",
        "stats": stats
    }


@router.get("/ping")
async def ping():
    """
    简单的ping检查，用于负载均衡器健康检查
    """
    return {"ping": "pong"} 