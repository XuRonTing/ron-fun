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
- 数据统计分析

## 快速开始

### 克隆仓库

```bash
git clone https://github.com/XuRonTing/ron-fun.git
cd ron-fun
```

### 后端启动

```bash
# 进入后端目录
cd ron-fun-project/ron-fun-backend

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload
```

### 前端启动

```bash
# 进入前端目录
cd ron-fun-project/packages/client

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 部署

项目支持使用Docker进行容器化部署，详见部署文档。

## 许可证

MIT
