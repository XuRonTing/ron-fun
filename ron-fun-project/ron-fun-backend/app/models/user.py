from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.models.base import Base as CustomBase

class User(Base, CustomBase):
    """
    用户模型
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="电子邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号码")
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    remaining_points = Column(Integer, default=0, nullable=False)
    total_points = Column(Integer, default=0, nullable=False)
    user_profile_picture = Column(String(255), nullable=True)
    vip_level = Column(Integer, default=0, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    user_status = Column(Integer, default=1, nullable=False)  # 1: 正常, 2: 禁用

    # 关联关系
    point_records = relationship("PointRecord", back_populates="user")
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")
    banner_clicks = relationship("BannerClick", back_populates="user")

    # 认证相关
    hashed_password = Column(String(128), nullable=False, comment="加密后的密码")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否为超级管理员")
    
    # 用户额外信息
    avatar = Column(String(255), nullable=True, comment="头像URL")
    nickname = Column(String(50), nullable=True, comment="昵称")
    bio = Column(Text, nullable=True, comment="个人简介")
    
    # 积分系统
    points = Column(Integer, default=0, comment="积分")
    total_points = Column(Integer, default=0, comment="累计获得的积分")
    used_points = Column(Integer, default=0, comment="已使用的积分")
    
    # 关联
    lottery_records = relationship("LotteryRecord", back_populates="user")
    addresses = relationship("Address", back_populates="user")
    point_logs = relationship("PointLog", back_populates="user")
    application_clicks = relationship("ApplicationClick", back_populates="user")