from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建SQLAlchemy引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,  # 是否打印SQL语句
    pool_pre_ping=True,  # 连接池预检查连接
    connect_args={"check_same_thread": False} if settings.SQLALCHEMY_DATABASE_URI and settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}
)

# 创建会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类模型
Base = declarative_base()

# 依赖项，提供数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 