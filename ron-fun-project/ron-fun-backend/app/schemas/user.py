from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import re

# 用户基础模式
class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    phone: Optional[str] = Field(None, description="手机号码")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    
    @validator("phone")
    def validate_phone(cls, v):
        if v is not None and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v

# 数据库中的用户信息
class UserInDB(UserBase):
    id: int
    remaining_points: int
    total_points: int
    created_at: datetime
    updated_at: datetime
    password: str

    class Config:
        orm_mode = True

# API响应中的用户信息（不包含密码）
class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: int
    is_active: bool
    is_superuser: bool
    points: int = 0
    
    class Config:
        orm_mode = True

# 用户分页查询参数
class UserFilter(BaseModel):
    username: Optional[str] = None
    is_admin: Optional[bool] = None
    user_status: Optional[int] = None
    vip_level: Optional[int] = None

class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(..., min_length=6, description="密码")
    password_confirm: str = Field(..., description="确认密码")
    
    @validator("password_confirm")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("两次输入的密码不一致")
        return v

class UserUpdate(BaseModel):
    """
    用户更新模型
    """
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    phone: Optional[str] = Field(None, description="手机号码")
    
    @validator("phone")
    def validate_phone(cls, v):
        if v is not None and not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v 