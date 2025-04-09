# Ron.fun 部署指南

本文档提供了 Ron.fun 项目的详细部署步骤和最佳实践。

## 目录
- [环境准备](#环境准备)
- [部署流程](#部署流程)
- [配置管理](#配置管理)
- [安全措施](#安全措施)
- [监控与日志](#监控与日志)
- [备份与恢复](#备份与恢复)
- [常见问题解决](#常见问题解决)

## 环境准备

### 系统要求
- **操作系统**: Ubuntu 20.04 LTS 或更高版本
- **CPU**: 2核心+ (生产环境建议4核心+)
- **内存**: 4GB+ (生产环境建议8GB+)
- **存储**: 50GB+ (取决于数据量)
- **网络**: 公网IP，域名（可选）

### 软件依赖
- Docker 20.10.0+
- Docker Compose 2.0.0+
- Git

### 网络配置
- 开放以下端口：
  - 80 (HTTP)
  - 443 (HTTPS)
  - 22 (SSH)

## 部署流程

### 1. 安装 Docker 和 Docker Compose

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 获取项目代码

```bash
# 克隆项目代码
git clone https://github.com/your-organization/ron-fun.git
cd ron-fun/ron-fun-project/ron-fun-backend
```

### 3. 配置环境变量

```bash
# 复制并编辑环境配置
cp deploy/.env.prod .env
nano .env
```

根据环境修改以下关键配置：
- `MYSQL_PASSWORD`: 数据库密码
- `SECRET_KEY`: JWT令牌密钥
- `BACKEND_CORS_ORIGINS`: 允许的CORS域名

### 4. 启动服务

```bash
cd deploy
docker-compose up -d
```

### 5. 初始化数据库（首次部署）

数据库初始化脚本会在容器首次启动时自动执行。如需手动执行：

```bash
docker-compose exec db mysql -u root -p ronfun < mysql/init/init.sql
```

### 6. 验证部署

```bash
# 检查所有容器是否正常运行
docker-compose ps

# 测试API服务
curl http://localhost/api/v1/health
```

## 配置管理

### 环境配置文件

项目使用`.env`文件管理环境变量。不同环境的配置模板：

- 开发环境: `deploy/.env.dev`
- 测试环境: `deploy/.env.test`
- 生产环境: `deploy/.env.prod`

### 密钥管理

在生产环境中，敏感信息（如数据库密码、密钥等）应使用密钥管理系统进行管理，避免明文存储。

## 安全措施

### HTTPS 配置

在生产环境中，强烈建议启用HTTPS：

1. 获取SSL证书（可使用Let's Encrypt）
2. 将证书文件放置在`deploy/nginx/ssl/`目录下
3. 修改Nginx配置以启用HTTPS

### 数据库安全

- 限制数据库只接受内部网络访问
- 定期更改数据库密码
- 最小权限原则设置数据库用户权限

## 监控与日志

### 日志收集

所有服务的日志都可以通过Docker Compose查看：

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs api
```

### 监控设置

建议集成Prometheus和Grafana进行系统监控：

1. 部署Prometheus容器
2. 配置FastAPI应用暴露metrics端点
3. 设置Grafana面板显示关键指标

## 备份与恢复

### 数据库备份

设置定期备份脚本：

```bash
#!/bin/bash
BACKUP_DIR=/path/to/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db mysqldump -u root -p ronfun > $BACKUP_DIR/ronfun_$TIMESTAMP.sql
```

添加到crontab定期执行：

```
0 2 * * * /path/to/backup_script.sh  # 每天凌晨2点执行备份
```

### 数据恢复

从备份文件恢复数据：

```bash
docker-compose exec -T db mysql -u root -p ronfun < /path/to/backup_file.sql
```

## 常见问题解决

### 容器启动失败

检查日志查找错误：

```bash
docker-compose logs [service_name]
```

### 数据库连接问题

检查数据库服务是否正常运行，以及环境变量配置是否正确：

```bash
# 检查数据库容器
docker-compose ps db

# 验证数据库连接
docker-compose exec api python -c "from app.db.session import engine; from sqlalchemy import text; with engine.connect() as conn: result = conn.execute(text('SELECT 1')); print(result.fetchone())"
```

### 文件权限问题

确保数据卷目录具有正确的权限：

```bash
sudo chown -R 1000:1000 /path/to/data/volumes
``` 