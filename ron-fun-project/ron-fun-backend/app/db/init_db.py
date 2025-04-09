import logging
from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.core.config import settings
from app.models import User, VIP
from app.services.auth import get_password_hash

logger = logging.getLogger(__name__)

# 初始化数据库表
def init_db(db: Session) -> None:
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 检查是否需要创建初始数据
    create_initial_data(db)

# 创建初始数据
def create_initial_data(db: Session) -> None:
    # 创建初始管理员用户
    create_initial_admin(db)
    
    # 创建VIP等级
    create_vip_levels(db)

# 创建初始管理员用户
def create_initial_admin(db: Session) -> None:
    # 检查是否已存在管理员
    admin = db.query(User).filter(User.is_admin == True).first()
    if admin:
        logger.info("管理员用户已存在，跳过创建")
        return
    
    # 创建管理员用户
    admin_user = User(
        username="admin",
        password=get_password_hash("admin123"),  # 默认密码，首次登录后应该修改
        is_admin=True,
        remaining_points=10000,
        total_points=10000,
        user_profile_picture="https://www.rongting.fun/avatar/default.png",
        user_status=1  # 正常状态
    )
    
    db.add(admin_user)
    db.commit()
    logger.info("初始管理员用户创建成功")

# 创建VIP等级
def create_vip_levels(db: Session) -> None:
    # 检查是否已存在VIP等级
    vip_count = db.query(VIP).count()
    if vip_count > 0:
        logger.info("VIP等级已存在，跳过创建")
        return
    
    # 创建默认VIP等级
    vip_levels = [
        VIP(vip_name="普通用户", vip_level=0, vip_total_point=0),
        VIP(vip_name="青铜会员", vip_level=1, vip_total_point=1000),
        VIP(vip_name="白银会员", vip_level=2, vip_total_point=5000),
        VIP(vip_name="黄金会员", vip_level=3, vip_total_point=10000),
        VIP(vip_name="钻石会员", vip_level=4, vip_total_point=50000),
        VIP(vip_name="至尊会员", vip_level=5, vip_total_point=100000),
    ]
    
    db.add_all(vip_levels)
    db.commit()
    logger.info("初始VIP等级创建成功") 