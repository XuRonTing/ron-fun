import os
import sys
import uvicorn
import importlib.util
import importlib.metadata
import subprocess
from pathlib import Path

# 检查并安装必要的依赖
required_packages = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pydantic",
    "pydantic-settings",
    "python-jose",
    "passlib",
    "python-multipart",
    "python-dotenv",
    "aiofiles",
    "jinja2"
]

def check_and_install_packages():
    print("检查依赖包...")
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.metadata.distribution(package)
        except importlib.metadata.PackageNotFoundError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"安装缺失的依赖包: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("依赖包安装完成!")
    else:
        print("所有依赖包已安装!")

def setup_demo_environment():
    # 创建必要的目录
    os.makedirs("app/static", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # 创建demo.html文件如果不存在
    demo_html_path = Path("app/static/demo.html")
    if not demo_html_path.exists():
        print("创建示例HTML文件...")
        with open(demo_html_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ron.fun - 演示版</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #605ff0;
            text-align: center;
        }
        .card {
            margin-top: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background-color: #fff;
        }
        .btn {
            display: inline-block;
            background-color: #605ff0;
            color: white;
            padding: 10px 15px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ron.fun 演示版</h1>
        
        <div class="card">
            <h2>API文档</h2>
            <p>查看API文档了解更多接口信息。</p>
            <a href="/docs" class="btn">查看API文档</a>
        </div>
        
        <div class="card">
            <h2>演示说明</h2>
            <p>由于演示环境使用SQLite数据库，部分功能可能无法完全展示。完整功能需配置MySQL数据库和进行数据迁移。</p>
        </div>
        
        <div class="card">
            <h2>可用功能</h2>
            <ul>
                <li>用户认证</li>
                <li>抽奖模块</li>
                <li>积分商城</li>
                <li>首页Banner和应用</li>
            </ul>
        </div>
    </div>
</body>
</html>""")

if __name__ == "__main__":
    # 检查并安装依赖
    check_and_install_packages()
    
    # 设置演示环境
    setup_demo_environment()
    
    # 运行应用
    print("启动应用服务器...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True) 