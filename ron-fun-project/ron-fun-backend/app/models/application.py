from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base
from app.models.base import Base as CustomBase

class Application(Base, CustomBase):
    __tablename__ = "applications"

    app_id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String(100), nullable=False, index=True)
    app_introduction = Column(String(500), nullable=True)
    app_icon = Column(String(255), nullable=True)
    app_link = Column(String(255), nullable=False)
    app_ordering = Column(Integer, nullable=False, default=0)  # 排序权重
    app_is_on_sale = Column(Boolean, nullable=False, default=True)  # 是否上架
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # 链接
    link_type = Column(String(50), nullable=False, comment="链接类型：url, internal等")
    link_url = Column(String(255), nullable=True, comment="链接URL")
    
    # 状态和排序
    is_active = Column(Boolean, default=True, comment="是否激活")
    sort_order = Column(Integer, default=0, comment="排序值，数值越大越靠前")
    
    # 展示位置
    position = Column(String(50), default="home", comment="展示位置：home首页, sidebar侧边栏等")
    
    # 统计
    view_count = Column(Integer, default=0, comment="浏览次数")
    click_count = Column(Integer, default=0, comment="点击次数")
    
    # 关联点击记录
    clicks = relationship("ApplicationClick", back_populates="application")

class ApplicationClick(Base, CustomBase):
    """
    应用点击记录
    """
    # 关联应用
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, comment="应用ID")
    application = relationship("Application", back_populates="clicks")
    
    # 关联用户（可能是未登录用户）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    user = relationship("User", back_populates="application_clicks")
    
    # 设备信息
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(255), nullable=True, comment="用户代理")
    device_type = Column(String(50), nullable=True, comment="设备类型：mobile, desktop等") 