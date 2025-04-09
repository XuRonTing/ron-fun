# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libmariadb-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY pyproject.toml .
COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app
COPY scripts ./scripts
COPY alembic ./alembic

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传和日志目录
RUN mkdir -p /app/uploads /app/logs
RUN chmod 777 /app/uploads /app/logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动应用
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"] 