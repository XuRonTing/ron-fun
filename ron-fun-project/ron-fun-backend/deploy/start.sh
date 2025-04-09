#!/bin/bash
set -e

# 定义日志函数
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# 等待MySQL数据库启动
wait_for_db() {
    log "等待MySQL数据库启动..."
    
    host="${MYSQL_SERVER:-db}"
    port="${MYSQL_PORT:-3306}"
    user="${MYSQL_USER:-ron_fun}"
    password="${MYSQL_PASSWORD:-ron_fun_password}"
    
    for i in {1..30}; do
        if mysqladmin ping -h "$host" -P "$port" -u "$user" --password="$password" --silent; then
            log "数据库连接成功"
            return 0
        fi
        log "等待数据库连接... $i/30"
        sleep 2
    done
    
    log "无法连接到数据库，退出"
    exit 1
}

# 应用数据库迁移
apply_migrations() {
    log "应用数据库迁移..."
    cd /app
    alembic upgrade head
    log "数据库迁移完成"
}

# 初始化数据（如有需要）
init_data() {
    if [ "${INIT_DATA:-false}" = "true" ]; then
        log "初始化数据..."
        python -m app.scripts.init_data
        log "数据初始化完成"
    else
        log "跳过数据初始化"
    fi
}

# 主函数
main() {
    log "启动Ron.fun后端服务..."
    
    # 等待数据库
    wait_for_db
    
    # 应用迁移
    apply_migrations
    
    # 初始化数据
    init_data
    
    # 启动API服务
    log "启动FastAPI服务"
    if [ "${ENVIRONMENT:-production}" = "development" ]; then
        log "以开发模式启动"
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    else
        log "以生产模式启动"
        gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w ${WORKERS:-4} --bind 0.0.0.0:8000
    fi
}

# 执行主函数
main 