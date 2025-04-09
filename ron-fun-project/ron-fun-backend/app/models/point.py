from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.session import Base
from app.models.base import Base as CustomBase

class PointRecord(Base):
    __tablename__ = "point_records"

    record_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reason = Column(Integer, nullable=False, index=True)  # 1：抽奖消耗积分 2：抽奖增加积分 3：兑换商品 4：后台调整
    point_number = Column(Integer, nullable=False)  # 正数：增加 负数：减少
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=True, index=True)
    exchange_time = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关联关系
    user = relationship("User", back_populates="point_records")
    product = relationship("Product", back_populates="point_records")

class PointLog(Base, CustomBase):
    """
    积分记录模型
    """
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    user = relationship("User", back_populates="point_logs")
    
    # 积分变动
    points = Column(Integer, nullable=False, comment="积分变动数量，正为增加，负为减少")
    balance = Column(Integer, nullable=False, comment="变动后的积分余额")
    
    # 变动类型
    type = Column(String(50), nullable=False, comment="变动类型（如抽奖、兑换、签到等）")
    
    # 关联信息
    related_id = Column(Integer, nullable=True, comment="关联ID，如抽奖记录ID、订单ID等")
    related_type = Column(String(50), nullable=True, comment="关联类型")
    
    # 描述信息
    description = Column(String(255), nullable=True, comment="变动描述")
    
    # 操作人（管理员操作时）
    operator_id = Column(Integer, nullable=True, comment="操作人ID")
    operator_name = Column(String(50), nullable=True, comment="操作人姓名")
    
    # IP地址
    ip_address = Column(String(50), nullable=True, comment="IP地址") 