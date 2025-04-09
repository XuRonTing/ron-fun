# Ron.fun 项目部署文档

## 部署架构

Ron.fun 项目采用容器化部署方式，主要包含以下组件：

- **API服务**：FastAPI后端应用
- **MySQL数据库**：存储业务数据
- **Nginx**：提供反向代理和静态资源服务

## 部署环境要求

- **Docker**: 20.10.0+
- **Docker Compose**: 2.0.0+
- **服务器配置建议**：
  - CPU: 2核心+
  - 内存: 4GB+
  - 存储: 50GB+
  - 操作系统: Ubuntu 20.04 LTS 或更高版本

## 部署步骤

### 1. 准备环境

确保服务器已安装Docker和Docker Compose:

```bash
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version
```

### 2. 克隆代码仓库

```bash
git clone https://github.com/your-org/ron-fun.git
cd ron-fun/ron-fun-project/ron-fun-backend
```

### 3. 配置环境变量

复制示例环境配置文件并进行必要的修改：

```bash
cp deploy/.env.prod .env
```

修改`.env`文件中的敏感信息，特别是：
- MySQL密码
- JWT密钥
- CORS域名设置

### 4. 启动服务

使用Docker Compose启动所有服务：

```bash
cd deploy
docker-compose up -d
```

### 5. 验证部署

验证各服务是否正常运行：

```bash
# 检查容器状态
docker-compose ps

# 检查API服务日志
docker-compose logs api

# 测试API服务是否正常响应
curl http://localhost/api/v1/health
```

## 数据库管理

### 初始化数据

初始数据将在首次启动时通过`mysql/init/init.sql`脚本自动导入。

### 数据备份

设置定期备份MySQL数据：

```bash
# 备份MySQL数据
docker-compose exec db mysqldump -u root -p ronfun > backup_$(date +%Y%m%d).sql
```

## 维护与升级

### 服务重启

重启所有服务：

```bash
docker-compose restart
```

重启单个服务：

```bash
docker-compose restart api
```

### 升级应用

更新代码并重新构建服务：

```bash
git pull
docker-compose build api
docker-compose up -d
```

## 常见问题处理

### 数据库连接问题

检查数据库容器是否正常运行：

```bash
docker-compose ps db
```

检查数据库日志：

```bash
docker-compose logs db
```

### API服务无法访问

检查Nginx配置和日志：

```bash
docker-compose logs nginx
```

## 安全建议

1. 定期更新容器镜像和系统依赖
2. 启用HTTPS并配置SSL证书
3. 限制数据库访问仅允许内部网络
4. 定期更换密钥和密码
5. 启用防火墙，只开放必要端口
6. 设置定期自动备份 