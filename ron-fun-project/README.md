# Ron.fun 项目

Ron.fun是一个包含H5前端和后台管理系统的完整web应用，主要功能包括用户管理、抽奖游戏、积分商城和应用/Banner管理等。

## 项目结构

项目采用Monorepo管理方式，包含以下子项目：

```
ron-fun/
├── packages/                # 子包目录
│   ├── client/              # H5客户端
│   ├── admin/               # 管理后台
│   └── shared/              # 共享代码
└── ron-fun-backend/         # 后端API服务
```

## 技术栈

### 前端
- React 18 + TypeScript
- Vite 4 构建工具
- @headlessui/react + heroicons UI组件
- Zustand 状态管理
- React Router 6 路由
- axios 1.6 请求库
- postcss-px-to-viewport 移动端适配
- framer-motion 动效库

### 后端
- Python 3.12
- FastAPI 框架
- SQLAlchemy ORM
- Alembic 数据迁移
- JWT 认证
- MySQL 8.0 数据库

## 开发指南

### 环境要求
- Node.js 18+
- Python 3.12+
- MySQL 8.0+
- Docker (可选，用于容器化部署)

### 开发环境设置

1. 克隆仓库
```bash
git clone https://github.com/yourusername/ron-fun.git
cd ron-fun
```

2. 安装前端依赖
```bash
npm install
```

3. 安装后端依赖
```bash
cd ron-fun-backend
pip install -r requirements.txt
# 或使用Poetry
poetry install
```

4. 设置环境变量
- 创建前端环境变量文件 `.env.development`
- 创建后端环境变量文件 `.env`

5. 启动开发服务器

前端：
```bash
# 启动H5客户端
npm run dev:client

# 启动管理后台
npm run dev:admin
```

后端：
```bash
cd ron-fun-backend
uvicorn app.main:app --reload
```

## 文档

- [项目架构文档](docs/architecture.md)
- [API接口文档](docs/api.md)
- [部署指南](docs/deployment.md)
- [开发规范](docs/coding-standards.md)

## 项目进度

请查看[任务清单](todo.md)了解项目当前进度。

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE)

## 联系方式

- 项目维护者: Your Name
- 邮箱: your.email@example.com 