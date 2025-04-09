from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re

# 令牌模式
class Token(BaseModel):
    access_token: str
    token_type: str

# 令牌载荷
class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

# 用户登录模式
class UserLogin(BaseModel):
    username: str
    password: str

# 用户创建模式
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    phone_number: Optional[str] = None

    @validator("phone_number")
    def phone_number_validator(cls, v):
        if v is not None:
            if not re.match(r"^1[3-9]\d{9}$", v):
                raise ValueError("手机号格式不正确")
        return v

# 用户更新模式
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone_number: Optional[str] = None
    user_profile_picture: Optional[str] = None

    @validator("phone_number")
    def phone_number_validator(cls, v):
        if v is not None:
            if not re.match(r"^1[3-9]\d{9}$", v):
                raise ValueError("手机号格式不正确")
        return v

# 密码修改模式
class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6) 