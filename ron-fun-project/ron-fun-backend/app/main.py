from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
import os

# 创建必要的目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("app/static", exist_ok=True)  # 创建静态文件目录

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    # 添加root_path配置，支持子路径访问
    root_path="/ron-fun" if os.getenv("ENABLE_ROOT_PATH", "false").lower() == "true" else "",
)

# 设置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": f"欢迎访问 {settings.PROJECT_NAME} 演示版本"}

@app.get("/demo")
async def demo():
    # 重定向到静态演示页面
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/simple_demo.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True) 