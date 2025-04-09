from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import authenticate_user, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    Args:
        form_data: 登录表单
        db: 数据库会话
        
    Returns:
        Token: 包含访问令牌和令牌类型的响应
        
    Raises:
        HTTPException: 如果认证失败
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    
    Args:
        user_in: 用户注册信息
        db: 数据库会话
        
    Returns:
        UserResponse: 用户响应
        
    Raises:
        HTTPException: 如果用户名已存在
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_in.email:
        existing_email = db.query(User).filter(User.email == user_in.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 检查手机号是否已存在
    if user_in.phone:
        existing_phone = db.query(User).filter(User.phone == user_in.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
    
    # 创建新用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        nickname=user_in.nickname,
        avatar=user_in.avatar,
        bio=user_in.bio
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        UserResponse: 用户响应
    """
    return current_user 