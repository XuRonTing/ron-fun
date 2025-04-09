from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_active_superuser, get_optional_current_user
from app.models.user import User
from app.models.banner import Banner
from app.models.application import Application
from app.schemas.home import (
    BannerResponse, ApplicationResponse, HomeDataResponse,
    BannerCreate, BannerUpdate, ApplicationCreate, ApplicationUpdate
)
from app.services.home_service import home_service
from app.core.config import settings

router = APIRouter()

# 首页数据接口
@router.get("", response_model=HomeDataResponse, summary="获取首页数据")
async def get_home_data(
    position: str = "home",
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    获取首页数据，包括Banner和应用列表
    
    Args:
        position: 展示位置，默认首页
        db: 数据库会话
        current_user: 当前用户（可选）
        
    Returns:
        首页数据
    """
    # 获取Banner列表
    banners = home_service.get_banners(db, position)
    
    # 获取应用列表
    applications = home_service.get_applications(db, position)
    
    # 组装响应数据
    return {
        "banners": banners,
        "applications": applications
    }

# Banner相关接口
@router.get("/banners", response_model=List[BannerResponse], summary="获取Banner列表")
async def get_banners(
    position: str = "home",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
    device_type: str = Query("mobile", description="设备类型: mobile, desktop"),
    request: Request = None
):
    """
    获取Banner列表
    
    Args:
        position: 展示位置
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前用户（可选）
        device_type: 设备类型
        request: 请求对象
        
    Returns:
        Banner列表
    """
    banner_service = BannerService(db)
    # 记录Banner展示
    banners = banner_service.get_active_banners(device_type, position)
    if request:
        for banner in banners:
            banner_service.record_banner_view(banner.id, request)
    return banners

@router.get("/banners/{banner_id}", response_model=BannerResponse, summary="获取Banner详情")
async def get_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    获取Banner详情
    
    Args:
        banner_id: Banner ID
        db: 数据库会话
        current_user: 当前用户（可选）
        
    Returns:
        Banner详情
    """
    banner = home_service.get_banner(db, banner_id)
    # 增加浏览次数
    banner.view_count += 1
    db.commit()
    
    return banner

@router.post("/banners/click/{banner_id}", summary="记录Banner点击")
async def record_banner_click(
    banner_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    记录Banner点击
    
    Args:
        banner_id: Banner ID
        request: 请求对象
        db: 数据库会话
        current_user: 当前用户（可选）
        
    Returns:
        成功消息
    """
    home_service.record_banner_click(db, banner_id, current_user, request)
    return {"message": "点击已记录"}

@router.post("/banners", response_model=BannerResponse, summary="创建Banner")
async def create_banner(
    banner_in: BannerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    创建Banner（仅限管理员）
    
    Args:
        banner_in: Banner创建请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        创建的Banner
    """
    # 创建Banner
    banner = Banner(**banner_in.dict())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    
    return banner

@router.put("/banners/{banner_id}", response_model=BannerResponse, summary="更新Banner")
async def update_banner(
    banner_id: int,
    banner_in: BannerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    更新Banner（仅限管理员）
    
    Args:
        banner_id: Banner ID
        banner_in: Banner更新请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        更新后的Banner
    """
    # 获取Banner
    banner = home_service.get_banner(db, banner_id)
    
    # 更新字段
    update_data = banner_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(banner, field, value)
    
    db.commit()
    db.refresh(banner)
    
    return banner

@router.delete("/banners/{banner_id}", summary="删除Banner")
async def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    删除Banner（仅限管理员）
    
    Args:
        banner_id: Banner ID
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        删除结果
    """
    # 获取Banner
    banner = home_service.get_banner(db, banner_id)
    
    # 软删除
    banner.is_deleted = True
    db.commit()
    
    return {"message": "Banner已删除"}

# 应用相关接口
@router.get("/applications", response_model=List[ApplicationResponse], summary="获取应用列表")
async def get_applications(
    position: str = "home",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    获取应用列表
    
    Args:
        position: 展示位置
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前用户（可选）
        
    Returns:
        应用列表
    """
    applications = home_service.get_applications(db, position, skip, limit)
    return applications

@router.get("/applications/{app_id}", response_model=ApplicationResponse, summary="获取应用详情")
async def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    获取应用详情
    
    Args:
        app_id: 应用ID
        db: 数据库会话
        current_user: 当前用户（可选）
        
    Returns:
        应用详情
    """
    application = home_service.get_application(db, app_id)
    # 增加浏览次数
    application.view_count += 1
    db.commit()
    
    return application

@router.post("/applications/click/{app_id}", summary="记录应用点击")
async def record_application_click(
    app_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    记录应用点击
    
    Args:
        app_id: 应用ID
        request: 请求对象
        db: 数据库会话
        current_user: 当前用户（可选）
        
    Returns:
        成功消息
    """
    home_service.record_application_click(db, app_id, current_user, request)
    return {"message": "点击已记录"}

@router.post("/applications", response_model=ApplicationResponse, summary="创建应用")
async def create_application(
    app_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    创建应用（仅限管理员）
    
    Args:
        app_in: 应用创建请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        创建的应用
    """
    # 创建应用
    application = Application(**app_in.dict())
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application

@router.put("/applications/{app_id}", response_model=ApplicationResponse, summary="更新应用")
async def update_application(
    app_id: int,
    app_in: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    更新应用（仅限管理员）
    
    Args:
        app_id: 应用ID
        app_in: 应用更新请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        更新后的应用
    """
    # 获取应用
    application = home_service.get_application(db, app_id)
    
    # 更新字段
    update_data = app_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    
    return application

@router.delete("/applications/{app_id}", summary="删除应用")
async def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    删除应用（仅限管理员）
    
    Args:
        app_id: 应用ID
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        删除结果
    """
    # 获取应用
    application = home_service.get_application(db, app_id)
    
    # 软删除
    application.is_deleted = True
    db.commit()
    
    return {"message": "应用已删除"}

@router.get("/health", response_model=dict)
async def health_check():
    """
    健康检查接口，用于Docker健康检查
    """
    return {"status": "healthy", "version": settings.PROJECT_VERSION} 