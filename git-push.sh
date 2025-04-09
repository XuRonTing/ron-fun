#!/bin/bash
# Ron.fun项目GitHub推送脚本
# 用于将项目推送到GitHub仓库
# 确保脚本使用UTF-8编码

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 打印信息函数
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# GitHub仓库URL
REPO_URL="https://github.com/XuRonTing/ron-fun.git"

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    error "Git未安装。请先安装Git: https://git-scm.com/downloads"
fi

# 创建.gitignore文件
info "创建.gitignore文件..."
cat > .gitignore << EOL
# 系统文件
.DS_Store
Thumbs.db

# 编辑器目录
.idea/
.vscode/
*.sublime-*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# 依赖目录
node_modules/
venv/
.env

# 日志
*.log
logs/

# 临时文件
.tmp/
temp/

# 上传文件目录
uploads/

# 数据库
*.sqlite
*.db

# Docker
deploy_temp/
ron-fun-deploy.tar.gz

# 密码和敏感信息
deploy.sh
deploy.bat
EOL

# 创建README.md文件
info "创建README.md文件..."
cat > README.md << EOL
# Ron.fun 项目

Ron.fun是一个综合性用户积分平台，专注于提供积分管理、抽奖活动和积分商城服务，旨在提高用户参与度和活跃度。

## 项目架构

项目采用前后端分离架构：
- 后端：FastAPI + SQLAlchemy + MySQL
- 前端：Vue.js + Vant/Element Plus

## 核心功能模块

- 用户账户管理
- 积分系统
- 抽奖活动（九宫格、大转盘）
- 积分商城
- 应用推荐
- Banner管理
- 数据统计分析

## 快速开始

### 克隆仓库

\`\`\`bash
git clone https://github.com/XuRonTing/ron-fun.git
cd ron-fun
\`\`\`

### 后端启动

\`\`\`bash
# 进入后端目录
cd ron-fun-project/ron-fun-backend

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload
\`\`\`

### 前端启动

\`\`\`bash
# 进入前端目录
cd ron-fun-project/packages/client

# 安装依赖
npm install

# 启动开发服务器
npm run dev
\`\`\`

## 部署

项目支持使用Docker进行容器化部署，详见部署文档。

## 许可证

MIT
EOL

# 初始化Git仓库
info "初始化Git仓库..."
if [ ! -d ".git" ]; then
    git init
    info "Git仓库初始化完成。"
else
    info "Git仓库已存在，跳过初始化步骤。"
fi

# 询问用户GitHub用户名和邮箱
read -p "请输入您的GitHub用户名: " github_username
read -p "请输入您的GitHub邮箱: " github_email

# 配置Git用户信息
git config user.name "$github_username"
git config user.email "$github_email"

# 添加远程仓库
info "添加远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# 添加所有文件到暂存区
info "添加文件到暂存区..."
git add .

# 提交更改
info "提交更改..."
git commit -m "初始化Ron.fun项目"

# 推送到GitHub
info "推送到GitHub..."
echo "正在推送代码到 $REPO_URL"
echo "您可能需要输入GitHub凭据..."

# 切换到main分支
git branch -M main

# 推送到GitHub
git push -u origin main

info "项目已成功推送到GitHub: $REPO_URL"
info "仓库地址: https://github.com/XuRonTing/ron-fun" 