from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base
from app.models.base import Base as CustomBase

class LotteryType(Base, CustomBase):
    """
    抽奖类型模型（九宫格、大转盘等）
    """
    name = Column(String(50), nullable=False, comment="抽奖类型名称")
    code = Column(String(50), nullable=False, unique=True, comment="抽奖类型代码")
    description = Column(Text, nullable=True, comment="抽奖类型描述")
    icon = Column(String(255), nullable=True, comment="抽奖类型图标")
    
    # 关联抽奖活动
    activities = relationship("LotteryActivity", back_populates="lottery_type")

class LotteryActivity(Base, CustomBase):
    """
    抽奖活动模型
    """
    title = Column(String(100), nullable=False, comment="活动标题")
    description = Column(Text, nullable=True, comment="活动描述")
    banner_image = Column(String(255), nullable=True, comment="活动横幅图片")
    
    # 活动时间范围
    start_time = Column(DateTime, nullable=False, default=datetime.now, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    
    # 活动状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 抽奖限制
    daily_limit = Column(Integer, default=0, comment="每日抽奖次数限制，0表示不限制")
    total_limit = Column(Integer, default=0, comment="总抽奖次数限制，0表示不限制")
    
    # 消耗积分
    points_cost = Column(Integer, default=0, comment="每次抽奖消耗的积分")
    
    # 抽奖类型关联
    lottery_type_id = Column(Integer, ForeignKey("lottery_types.id"), nullable=False, comment="抽奖类型ID")
    lottery_type = relationship("LotteryType", back_populates="activities")
    
    # 奖品设置
    prize_settings = Column(JSON, nullable=False, comment="奖品设置，包括奖品、概率等信息")
    
    # 关联抽奖记录
    records = relationship("LotteryRecord", back_populates="activity")

class LotteryRecord(Base, CustomBase):
    """
    抽奖记录模型
    """
    # 用户关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    user = relationship("User", back_populates="lottery_records")
    
    # 抽奖活动关联
    activity_id = Column(Integer, ForeignKey("lottery_activities.id"), nullable=False, comment="抽奖活动ID")
    activity = relationship("LotteryActivity", back_populates="records")
    
    # 奖品信息
    prize_id = Column(Integer, nullable=True, comment="奖品ID")
    prize_name = Column(String(100), nullable=True, comment="奖品名称")
    prize_type = Column(String(50), nullable=True, comment="奖品类型（积分、实物等）")
    prize_amount = Column(Integer, nullable=True, comment="奖品数量或积分值")
    prize_image = Column(String(255), nullable=True, comment="奖品图片")
    
    # 是否中奖
    is_win = Column(Boolean, default=False, comment="是否中奖")
    
    # 消耗积分
    points_cost = Column(Integer, default=0, comment="消耗的积分")
    
    # 兑换状态（实物奖品）
    is_exchanged = Column(Boolean, default=False, comment="是否已兑换")
    exchange_time = Column(DateTime, nullable=True, comment="兑换时间")
    
    # IP地址和设备信息
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(255), nullable=True, comment="用户代理信息")

class LotteryPrize(Base, CustomBase):
    """
    抽奖奖品模型（全局奖品库）
    """
    name = Column(String(100), nullable=False, comment="奖品名称")
    description = Column(Text, nullable=True, comment="奖品描述")
    image = Column(String(255), nullable=True, comment="奖品图片")
    
    # 奖品类型
    prize_type = Column(String(50), nullable=False, comment="奖品类型（积分、实物等）")
    prize_value = Column(Integer, default=0, comment="奖品价值（积分值或人民币价值，单位：分）")
    
    # 奖品数量
    total_count = Column(Integer, default=0, comment="奖品总数，0表示不限制")
    remaining_count = Column(Integer, default=0, comment="剩余数量")
    
    # 奖品状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 额外信息
    extra_data = Column(JSON, nullable=True, comment="额外信息，如兑换码等") 