from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.api.deps import get_db, get_current_active_superuser
from app.models.user import User
from app.models.product import Product, ProductCategory, Order, OrderItem
from app.models.application import Application, ApplicationClick
from app.models.banner import Banner, BannerClick
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate, OrderResponse
from app.schemas.application import ApplicationResponse, ApplicationCreate, ApplicationUpdate, ApplicationClickResponse
from app.schemas.banner import BannerResponse, BannerCreate, BannerUpdate, BannerClickResponse
from app.schemas.common import PaginatedResponse, DateRangeParams

router = APIRouter()

# ------------------- 用户管理 -------------------
@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[bool] = None
):
    """获取用户列表"""
    query = db.query(User)
    
    # 应用过滤条件
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.nickname.ilike(f"%{search}%")
            )
        )
    
    if status is not None:
        query = query.filter(User.is_active == status)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": users,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}/points", response_model=UserResponse)
async def adjust_user_points(
    user_id: int = Path(..., gt=0),
    points: int = Query(..., description="积分调整数量，正数为增加，负数为减少"),
    reason: str = Query(..., description="积分调整原因"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """调整用户积分"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查是否有足够的积分可以减少
    if points < 0 and user.points < abs(points):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户积分不足"
        )
    
    # 调整积分
    user.points += points
    if points > 0:
        user.total_points += points
    
    # 添加积分记录（如果有PointLog模型）
    # point_log = PointLog(
    #     user_id=user.id,
    #     points=points,
    #     reason=reason,
    #     created_by=current_user.id
    # )
    # db.add(point_log)
    
    db.commit()
    db.refresh(user)
    return user

# ------------------- 积分商城管理 -------------------
@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[bool] = None
):
    """获取商品列表"""
    query = db.query(Product)
    
    # 应用过滤条件
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if status is not None:
        query = query.filter(Product.is_active == status)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    products = query.order_by(Product.sort_order).offset(skip).limit(limit).all()
    
    return {
        "items": products,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """获取商品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    return product

@router.post("/products", response_model=ProductResponse)
async def create_product(
    product_create: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """创建商品"""
    # 检查分类是否存在
    category = db.query(ProductCategory).filter(ProductCategory.id == product_create.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    product = Product(**product_create.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_update: ProductUpdate,
    product_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """更新商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查分类是否存在
    if product_update.category_id is not None:
        category = db.query(ProductCategory).filter(ProductCategory.id == product_update.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
    
    for field, value in product_update.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.get("/orders", response_model=PaginatedResponse[OrderResponse])
async def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """获取订单列表"""
    query = db.query(Order)
    
    # 应用过滤条件
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": orders,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

# ------------------- 应用管理 -------------------
@router.get("/applications", response_model=PaginatedResponse[ApplicationResponse])
async def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[bool] = None
):
    """获取应用列表"""
    query = db.query(Application)
    
    # 应用过滤条件
    if search:
        query = query.filter(Application.name.ilike(f"%{search}%"))
    
    if status is not None:
        query = query.filter(Application.is_active == status)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    applications = query.order_by(Application.sort_order).offset(skip).limit(limit).all()
    
    return {
        "items": applications,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """获取应用详情"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="应用不存在"
        )
    return application

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    application_create: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """创建应用"""
    application = Application(**application_create.dict())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.put("/applications/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_update: ApplicationUpdate,
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """更新应用"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="应用不存在"
        )
    
    for field, value in application_update.dict(exclude_unset=True).items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    return application

@router.get("/applications/{application_id}/clicks", response_model=PaginatedResponse[ApplicationClickResponse])
async def get_application_clicks(
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """获取应用点击统计"""
    # 检查应用是否存在
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="应用不存在"
        )
    
    query = db.query(ApplicationClick).filter(ApplicationClick.application_id == application_id)
    
    # 应用过滤条件
    if start_date:
        query = query.filter(ApplicationClick.created_at >= start_date)
    
    if end_date:
        query = query.filter(ApplicationClick.created_at <= end_date)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    clicks = query.order_by(ApplicationClick.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": clicks,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/applications/statistics", response_model=List[dict])
async def get_application_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    days: int = Query(7, ge=1, le=30),
):
    """获取应用点击统计数据（按应用和日期分组）"""
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 查询每个应用每天的点击次数
    result = db.query(
        ApplicationClick.application_id,
        func.date(ApplicationClick.created_at).label("date"),
        func.count().label("count")
    ).filter(
        ApplicationClick.created_at.between(start_date, end_date)
    ).group_by(
        ApplicationClick.application_id,
        func.date(ApplicationClick.created_at)
    ).all()
    
    # 查询所有应用信息以获取名称
    applications = {app.id: app.name for app in db.query(Application.id, Application.name).all()}
    
    # 构建响应数据
    statistics = [
        {
            "application_id": item.application_id,
            "application_name": applications.get(item.application_id, "未知应用"),
            "date": item.date.strftime("%Y-%m-%d"),
            "count": item.count
        }
        for item in result
    ]
    
    return statistics

# ------------------- Banner管理 -------------------
@router.get("/banners", response_model=PaginatedResponse[BannerResponse])
async def get_banners(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[bool] = None,
    position: Optional[str] = None
):
    """获取Banner列表"""
    query = db.query(Banner)
    
    # 应用过滤条件
    if search:
        query = query.filter(Banner.title.ilike(f"%{search}%"))
    
    if status is not None:
        query = query.filter(Banner.is_active == status)
    
    if position:
        query = query.filter(Banner.position == position)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    banners = query.order_by(Banner.sort_order).offset(skip).limit(limit).all()
    
    return {
        "items": banners,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/banners/{banner_id}", response_model=BannerResponse)
async def get_banner(
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """获取Banner详情"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner不存在"
        )
    return banner

@router.post("/banners", response_model=BannerResponse)
async def create_banner(
    banner_create: BannerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """创建Banner"""
    banner = Banner(**banner_create.dict())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return banner

@router.put("/banners/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_update: BannerUpdate,
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """更新Banner"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner不存在"
        )
    
    for field, value in banner_update.dict(exclude_unset=True).items():
        setattr(banner, field, value)
    
    db.commit()
    db.refresh(banner)
    return banner

@router.get("/banners/{banner_id}/clicks", response_model=PaginatedResponse[BannerClickResponse])
async def get_banner_clicks(
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """获取Banner点击统计"""
    # 检查Banner是否存在
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner不存在"
        )
    
    query = db.query(BannerClick).filter(BannerClick.banner_id == banner_id)
    
    # 应用过滤条件
    if start_date:
        query = query.filter(BannerClick.created_at >= start_date)
    
    if end_date:
        query = query.filter(BannerClick.created_at <= end_date)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    clicks = query.order_by(BannerClick.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": clicks,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/banners/statistics", response_model=List[dict])
async def get_banner_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    days: int = Query(7, ge=1, le=30),
):
    """获取Banner点击统计数据（按Banner和日期分组）"""
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 查询每个Banner每天的点击次数
    result = db.query(
        BannerClick.banner_id,
        func.date(BannerClick.created_at).label("date"),
        func.count().label("count")
    ).filter(
        BannerClick.created_at.between(start_date, end_date)
    ).group_by(
        BannerClick.banner_id,
        func.date(BannerClick.created_at)
    ).all()
    
    # 查询所有Banner信息以获取标题
    banners = {banner.id: banner.title for banner in db.query(Banner.id, Banner.title).all()}
    
    # 构建响应数据
    statistics = [
        {
            "banner_id": item.banner_id,
            "banner_title": banners.get(item.banner_id, "未知Banner"),
            "date": item.date.strftime("%Y-%m-%d"),
            "count": item.count
        }
        for item in result
    ]
    
    return statistics 