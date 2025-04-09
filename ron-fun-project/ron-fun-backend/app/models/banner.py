from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.session import Base
from app.models.base import Base as CustomBase

class Banner(Base, CustomBase):
    """
    Banner模型
    """
    __tablename__ = "banners"

    banner_id = Column(Integer, primary_key=True, index=True)
    banner_name = Column(String(100), nullable=False, index=True)
    banner_image = Column(String(255), nullable=False)
    banner_link = Column(String(255), nullable=False)
    banner_order = Column(Integer, nullable=False, default=0)  # 排序权重
    banner_introduction = Column(String(500), nullable=True)
    banner_expiration = Column(DateTime, nullable=True)  # Banner过期时间
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关联关系
    clicks = relationship("BannerClick", back_populates="banner")
    
    # 新添加的列
    title = Column(String(100), nullable=False, comment="标题")
    description = Column(Text, nullable=True, comment="描述")
    image = Column(String(255), nullable=False, comment="图片URL")
    
    # 链接
    link_type = Column(String(50), nullable=False, comment="链接类型：url, product, activity等")
    link_url = Column(String(255), nullable=True, comment="链接URL")
    link_id = Column(Integer, nullable=True, comment="关联ID")
    
    # 状态和排序
    is_active = Column(Boolean, default=True, comment="是否激活")
    sort_order = Column(Integer, default=0, comment="排序值，数值越大越靠前")
    
    # 展示位置
    position = Column(String(50), default="home", comment="展示位置：home首页, mall商城等")
    
    # 时间
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    
    # 统计
    view_count = Column(Integer, default=0, comment="浏览次数")
    click_count = Column(Integer, default=0, comment="点击次数")

class BannerClick(Base, CustomBase):
    """
    Banner点击记录
    """
    __tablename__ = "banner_clicks"

    click_id = Column(Integer, primary_key=True, index=True)
    banner_id = Column(Integer, ForeignKey("banners.banner_id"), nullable=False, index=True)
    click_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    click_user_name = Column(String(50), nullable=True)
    click_time = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关联关系
    banner = relationship("Banner", back_populates="clicks")
    user = relationship("User", back_populates="banner_clicks")
    
    # 新添加的列
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(255), nullable=True, comment="用户代理")
    device_type = Column(String(50), nullable=True, comment="设备类型：mobile, desktop等") 