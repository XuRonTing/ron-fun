@echo off
chcp 65001 >nul
echo Ron.fun项目GitHub推送工具

REM 检查Git是否安装
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Git未安装。请先安装Git: https://git-scm.com/downloads
    pause
    exit /b 1
)

REM 创建.gitignore文件
echo 创建.gitignore文件...
(
echo # 系统文件
echo .DS_Store
echo Thumbs.db
echo.
echo # 编辑器目录
echo .idea/
echo .vscode/
echo *.sublime-*
echo.
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo env/
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo.
echo # 依赖目录
echo node_modules/
echo venv/
echo .env
echo.
echo # 日志
echo *.log
echo logs/
echo.
echo # 临时文件
echo .tmp/
echo temp/
echo.
echo # 上传文件目录
echo uploads/
echo.
echo # 数据库
echo *.sqlite
echo *.db
echo.
echo # Docker
echo deploy_temp/
echo ron-fun-deploy.tar.gz
echo.
echo # 密码和敏感信息
echo deploy.sh
echo deploy.bat
) > .gitignore

REM 创建README.md文件
echo 创建README.md文件...
(
echo # Ron.fun 项目
echo.
echo Ron.fun是一个综合性用户积分平台，专注于提供积分管理、抽奖活动和积分商城服务，旨在提高用户参与度和活跃度。
echo.
echo ## 项目架构
echo.
echo 项目采用前后端分离架构：
echo - 后端：FastAPI + SQLAlchemy + MySQL
echo - 前端：Vue.js + Vant/Element Plus
echo.
echo ## 核心功能模块
echo.
echo - 用户账户管理
echo - 积分系统
echo - 抽奖活动（九宫格、大转盘）
echo - 积分商城
echo - 应用推荐
echo - Banner管理
echo - 数据统计分析
echo.
echo ## 快速开始
echo.
echo ### 克隆仓库
echo.
echo ```bash
echo git clone https://github.com/XuRonTing/ron-fun.git
echo cd ron-fun
echo ```
echo.
echo ### 后端启动
echo.
echo ```bash
echo # 进入后端目录
echo cd ron-fun-project/ron-fun-backend
echo.
echo # 安装依赖
echo pip install -r requirements.txt
echo.
echo # 启动开发服务器
echo uvicorn app.main:app --reload
echo ```
echo.
echo ### 前端启动
echo.
echo ```bash
echo # 进入前端目录
echo cd ron-fun-project/packages/client
echo.
echo # 安装依赖
echo npm install
echo.
echo # 启动开发服务器
echo npm run dev
echo ```
echo.
echo ## 部署
echo.
echo 项目支持使用Docker进行容器化部署，详见部署文档。
echo.
echo ## 许可证
echo.
echo MIT
) > README.md

REM 初始化Git仓库
echo 初始化Git仓库...
if not exist .git (
    git init
    echo Git仓库初始化完成。
) else (
    echo Git仓库已存在，跳过初始化步骤。
)

REM 询问用户GitHub用户名和邮箱
set /p github_username=请输入您的GitHub用户名: 
set /p github_email=请输入您的GitHub邮箱: 

REM 配置Git用户信息
git config user.name "%github_username%"
git config user.email "%github_email%"

REM 添加远程仓库
echo 添加远程仓库...
git remote remove origin 2>nul
git remote add origin "https://github.com/XuRonTing/ron-fun.git"

REM 添加所有文件到暂存区
echo 添加文件到暂存区...
git add .

REM 提交更改
echo 提交更改...
git commit -m "初始化Ron.fun项目"

REM 推送到GitHub
echo 推送到GitHub...
echo 正在推送代码到 https://github.com/XuRonTing/ron-fun.git
echo 您可能需要输入GitHub凭据...

REM 切换到main分支
git branch -M main

REM 推送到GitHub
git push -u origin main

echo 项目已成功推送到GitHub: https://github.com/XuRonTing/ron-fun
pause 