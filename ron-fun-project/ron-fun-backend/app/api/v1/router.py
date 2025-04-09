from fastapi import APIRouter

# 导入各个模块的路由
from app.api.v1.endpoints import auth, users, products, lottery, points, applications, banners, files, home, admin, health

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(products.router, prefix="/products", tags=["商品管理"])
api_router.include_router(lottery.router, prefix="/lottery", tags=["抽奖管理"])
api_router.include_router(points.router, prefix="/points", tags=["积分管理"])
api_router.include_router(applications.router, prefix="/apps", tags=["应用管理"])
api_router.include_router(banners.router, prefix="/banners", tags=["Banner管理"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
api_router.include_router(home.router, prefix="/home", tags=["首页管理"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])
api_router.include_router(health.router, prefix="/health", tags=["健康检查"]) 