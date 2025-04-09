from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 抽奖活动基础模型
class LotteryActivityBase(BaseModel):
    title: str = Field(..., description="活动标题")
    description: Optional[str] = Field(None, description="活动描述")
    banner_image: Optional[str] = Field(None, description="活动横幅图片")
    lottery_type_id: int = Field(..., description="抽奖类型ID")
    points_cost: int = Field(0, description="每次抽奖消耗的积分")
    daily_limit: int = Field(0, description="每日抽奖次数限制，0表示不限制")
    total_limit: int = Field(0, description="总抽奖次数限制，0表示不限制")
    is_active: bool = Field(True, description="是否激活")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    
# 创建抽奖活动请求
class LotteryActivityCreate(LotteryActivityBase):
    prize_settings: Dict[str, Any] = Field(..., description="奖品设置，包括奖品、概率等信息")

# 更新抽奖活动请求
class LotteryActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, description="活动标题")
    description: Optional[str] = Field(None, description="活动描述")
    banner_image: Optional[str] = Field(None, description="活动横幅图片")
    points_cost: Optional[int] = Field(None, description="每次抽奖消耗的积分")
    daily_limit: Optional[int] = Field(None, description="每日抽奖次数限制，0表示不限制")
    total_limit: Optional[int] = Field(None, description="总抽奖次数限制，0表示不限制")
    is_active: Optional[bool] = Field(None, description="是否激活")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    prize_settings: Optional[Dict[str, Any]] = Field(None, description="奖品设置，包括奖品、概率等信息")

# 抽奖活动响应
class LotteryActivityResponse(LotteryActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    prize_settings: Dict[str, Any]
    
    class Config:
        orm_mode = True

# 抽奖类型基础模型
class LotteryTypeBase(BaseModel):
    name: str = Field(..., description="抽奖类型名称")
    code: str = Field(..., description="抽奖类型代码")
    description: Optional[str] = Field(None, description="抽奖类型描述")
    icon: Optional[str] = Field(None, description="抽奖类型图标")

# 创建抽奖类型请求
class LotteryTypeCreate(LotteryTypeBase):
    pass

# 更新抽奖类型请求
class LotteryTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, description="抽奖类型名称")
    description: Optional[str] = Field(None, description="抽奖类型描述")
    icon: Optional[str] = Field(None, description="抽奖类型图标")

# 抽奖类型响应
class LotteryTypeResponse(LotteryTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 抽奖奖品基础模型
class LotteryPrizeBase(BaseModel):
    name: str = Field(..., description="奖品名称")
    description: Optional[str] = Field(None, description="奖品描述")
    image: Optional[str] = Field(None, description="奖品图片")
    prize_type: str = Field(..., description="奖品类型（积分、实物等）")
    prize_value: int = Field(0, description="奖品价值（积分值或人民币价值，单位：分）")
    total_count: int = Field(0, description="奖品总数，0表示不限制")
    remaining_count: int = Field(0, description="剩余数量")
    is_active: bool = Field(True, description="是否激活")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外信息，如兑换码等")

# 创建抽奖奖品请求
class LotteryPrizeCreate(LotteryPrizeBase):
    pass

# 更新抽奖奖品请求
class LotteryPrizeUpdate(BaseModel):
    name: Optional[str] = Field(None, description="奖品名称")
    description: Optional[str] = Field(None, description="奖品描述")
    image: Optional[str] = Field(None, description="奖品图片")
    prize_value: Optional[int] = Field(None, description="奖品价值（积分值或人民币价值，单位：分）")
    total_count: Optional[int] = Field(None, description="奖品总数，0表示不限制")
    remaining_count: Optional[int] = Field(None, description="剩余数量")
    is_active: Optional[bool] = Field(None, description="是否激活")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外信息，如兑换码等")

# 抽奖奖品响应
class LotteryPrizeResponse(LotteryPrizeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 抽奖记录基础模型
class LotteryRecordBase(BaseModel):
    user_id: int = Field(..., description="用户ID")
    activity_id: int = Field(..., description="抽奖活动ID")
    prize_id: Optional[int] = Field(None, description="奖品ID")
    prize_name: Optional[str] = Field(None, description="奖品名称")
    prize_type: Optional[str] = Field(None, description="奖品类型（积分、实物等）")
    prize_amount: Optional[int] = Field(None, description="奖品数量或积分值")
    prize_image: Optional[str] = Field(None, description="奖品图片")
    is_win: bool = Field(False, description="是否中奖")
    points_cost: int = Field(0, description="消耗的积分")
    is_exchanged: bool = Field(False, description="是否已兑换")

# 抽奖记录响应
class LotteryRecordResponse(LotteryRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    exchange_time: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# 抽奖请求
class LotteryDrawRequest(BaseModel):
    activity_id: int = Field(..., description="抽奖活动ID") 