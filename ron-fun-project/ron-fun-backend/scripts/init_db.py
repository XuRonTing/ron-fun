#!/usr/bin/env python
import os
import sys
import logging

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.exc import SQLAlchemyError
from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    初始化数据库，创建所有表和初始数据
    """
    try:
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        logger.info("成功创建数据库表")
        
        # 创建初始超级管理员
        db = SessionLocal()
        
        # 检查超级管理员是否已存在
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@ronfun.com",
                nickname="系统管理员",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("成功创建超级管理员账号")
        else:
            logger.info("超级管理员账号已存在")
            
    except SQLAlchemyError as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        db.close()

def main() -> None:
    logger.info("正在初始化数据库...")
    init_db()
    logger.info("数据库初始化完成！")

if __name__ == "__main__":
    main() 