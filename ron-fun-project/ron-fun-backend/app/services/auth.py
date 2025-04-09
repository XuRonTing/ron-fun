from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate
from app.core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # 用户认证
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    # 注册用户
    async def register_user(self, user_data: UserCreate) -> User:
        # 检查用户名是否已存在
        if self.db.query(User).filter(User.username == user_data.username).first():
            raise ValueError("用户名已存在")
            
        # 检查手机号是否已存在
        if user_data.phone_number and self.db.query(User).filter(User.phone_number == user_data.phone_number).first():
            raise ValueError("手机号已存在")
            
        # 创建用户
        user = User(
            username=user_data.username,
            password=get_password_hash(user_data.password),
            phone_number=user_data.phone_number,
            remaining_points=0,
            total_points=0,
            user_profile_picture=f"https://www.rongting.fun/avatar/{user_data.username}.png",
            vip_level=0,
            is_admin=False,
            user_status=1  # 正常状态
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # 更新用户
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
            
        # 检查用户名是否已被其他用户使用
        if user_data.username and user_data.username != user.username:
            if self.db.query(User).filter(User.username == user_data.username).first():
                raise ValueError("用户名已存在")
            user.username = user_data.username
            
        # 检查手机号是否已被其他用户使用
        if user_data.phone_number and user_data.phone_number != user.phone_number:
            if self.db.query(User).filter(User.phone_number == user_data.phone_number).first():
                raise ValueError("手机号已存在")
            user.phone_number = user_data.phone_number
            
        # 更新头像
        if user_data.user_profile_picture:
            user.user_profile_picture = user_data.user_profile_picture
            
        self.db.commit()
        self.db.refresh(user)
        return user

    # 修改密码
    async def change_password(self, user_id: int, new_password: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
            
        user.password = get_password_hash(new_password)
        self.db.commit()

    # 创建访问令牌
    def create_access_token(self, user_id: int) -> str:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            subject=user_id,
            expires_delta=expires_delta
        )

    # 验证密码
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password) 