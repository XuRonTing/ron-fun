from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_active_superuser
from app.models.user import User
from app.models.product import Product, ProductCategory, Order, Address
from app.schemas.product import (
    ProductCategoryResponse, ProductResponse, OrderResponse, AddressResponse,
    ProductCreate, ProductUpdate, ProductCategoryCreate, ProductCategoryUpdate,
    OrderCreate, AddressCreate, AddressUpdate
)
from app.services.product_service import product_service

router = APIRouter()

# 商品分类相关接口
@router.get("/categories", response_model=List[ProductCategoryResponse], summary="获取商品分类列表")
async def get_categories(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取商品分类列表
    
    Args:
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        分类列表
    """
    categories = product_service.get_categories(db, skip, limit)
    return categories

@router.post("/categories", response_model=ProductCategoryResponse, summary="创建商品分类")
async def create_category(
    category_in: ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    创建商品分类（仅限管理员）
    
    Args:
        category_in: 分类创建请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        创建的分类
    """
    # 创建分类
    category = ProductCategory(**category_in.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

@router.put("/categories/{category_id}", response_model=ProductCategoryResponse, summary="更新商品分类")
async def update_category(
    category_id: int,
    category_in: ProductCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    更新商品分类（仅限管理员）
    
    Args:
        category_id: 分类ID
        category_in: 分类更新请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        更新后的分类
    """
    # 查找分类
    category = db.query(ProductCategory).filter(
        ProductCategory.id == category_id,
        ProductCategory.is_deleted == False
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 更新字段
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/categories/{category_id}", summary="删除商品分类")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    删除商品分类（仅限管理员）
    
    Args:
        category_id: 分类ID
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        删除结果
    """
    # 查找分类
    category = db.query(ProductCategory).filter(
        ProductCategory.id == category_id,
        ProductCategory.is_deleted == False
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 检查是否有关联的商品
    product_count = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_deleted == False
    ).count()
    
    if product_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类下存在商品，无法删除"
        )
    
    # 软删除
    category.is_deleted = True
    db.commit()
    
    return {"message": "分类已删除"}

# 商品相关接口
@router.get("", response_model=List[ProductResponse], summary="获取商品列表")
async def get_products(
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    is_recommended: Optional[bool] = None,
    is_hot: Optional[bool] = None,
    is_new: Optional[bool] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取商品列表
    
    Args:
        skip: 跳过记录数
        limit: 返回记录数
        category_id: 分类ID
        is_recommended: 是否推荐
        is_hot: 是否热门
        is_new: 是否新品
        keyword: 搜索关键词
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        商品列表
    """
    products = product_service.get_products(
        db, skip, limit, category_id, is_recommended, is_hot, is_new, keyword
    )
    return products

@router.get("/{product_id}", response_model=ProductResponse, summary="获取商品详情")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取商品详情
    
    Args:
        product_id: 商品ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        商品详情
    """
    product = product_service.get_product(db, product_id)
    return product

@router.post("", response_model=ProductResponse, summary="创建商品")
async def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    创建商品（仅限管理员）
    
    Args:
        product_in: 商品创建请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        创建的商品
    """
    # 检查分类是否存在
    if product_in.category_id:
        category = db.query(ProductCategory).filter(
            ProductCategory.id == product_in.category_id,
            ProductCategory.is_deleted == False
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
    
    # 创建商品
    product = Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.put("/{product_id}", response_model=ProductResponse, summary="更新商品")
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    更新商品（仅限管理员）
    
    Args:
        product_id: 商品ID
        product_in: 商品更新请求
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        更新后的商品
    """
    # 查找商品
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查分类是否存在
    if product_in.category_id:
        category = db.query(ProductCategory).filter(
            ProductCategory.id == product_in.category_id,
            ProductCategory.is_deleted == False
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
    
    # 更新字段
    update_data = product_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", summary="删除商品")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    删除商品（仅限管理员）
    
    Args:
        product_id: 商品ID
        db: 数据库会话
        current_user: 当前用户（管理员）
        
    Returns:
        删除结果
    """
    # 查找商品
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_deleted == False
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    
    # 检查是否有关联的订单
    order_count = db.query(Order).join(
        OrderItem, Order.id == OrderItem.order_id
    ).filter(
        OrderItem.product_id == product_id,
        Order.is_deleted == False
    ).count()
    
    if order_count > 0:
        # 如果有订单，仅修改状态
        product.status = 0  # 下架
        db.commit()
        return {"message": "商品已下架（存在订单，无法彻底删除）"}
    
    # 软删除
    product.is_deleted = True
    db.commit()
    
    return {"message": "商品已删除"}

# 订单相关接口
@router.post("/orders", response_model=OrderResponse, summary="创建订单")
async def create_order(
    order_in: OrderCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建订单（兑换商品）
    
    Args:
        order_in: 订单创建请求
        request: 请求对象
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        创建的订单
    """
    # 获取客户端信息
    client_info = {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }
    
    # 创建订单
    order = product_service.create_order(
        db, current_user, 
        order_in.product_id, order_in.quantity, 
        order_in.address_id, client_info
    )
    
    return order

@router.get("/orders", response_model=List[OrderResponse], summary="获取用户订单列表")
async def get_orders(
    status: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户订单列表
    
    Args:
        status: 订单状态
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        订单列表
    """
    orders = product_service.get_user_orders(db, current_user.id, status, skip, limit)
    return orders

@router.get("/orders/{order_id}", response_model=OrderResponse, summary="获取订单详情")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取订单详情
    
    Args:
        order_id: 订单ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        订单详情
    """
    # 查找订单
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
        Order.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    return order

# 地址相关接口
@router.get("/addresses", response_model=List[AddressResponse], summary="获取用户地址列表")
async def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户地址列表
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        地址列表
    """
    addresses = db.query(Address).filter(
        Address.user_id == current_user.id,
        Address.is_deleted == False
    ).order_by(
        Address.is_default.desc(),
        Address.created_at.desc()
    ).all()
    
    return addresses

@router.post("/addresses", response_model=AddressResponse, summary="创建地址")
async def create_address(
    address_in: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建地址
    
    Args:
        address_in: 地址创建请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        创建的地址
    """
    # 如果设置为默认地址，需要将其他地址设为非默认
    if address_in.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True,
            Address.is_deleted == False
        ).update({"is_default": False})
    
    # 创建地址
    address = Address(**address_in.dict(), user_id=current_user.id)
    db.add(address)
    db.commit()
    db.refresh(address)
    
    return address

@router.put("/addresses/{address_id}", response_model=AddressResponse, summary="更新地址")
async def update_address(
    address_id: int,
    address_in: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新地址
    
    Args:
        address_id: 地址ID
        address_in: 地址更新请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        更新后的地址
    """
    # 查找地址
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
        Address.is_deleted == False
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地址不存在"
        )
    
    # 如果设置为默认地址，需要将其他地址设为非默认
    if address_in.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != address_id,
            Address.is_default == True,
            Address.is_deleted == False
        ).update({"is_default": False})
    
    # 更新字段
    update_data = address_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)
    
    db.commit()
    db.refresh(address)
    
    return address

@router.delete("/addresses/{address_id}", summary="删除地址")
async def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除地址
    
    Args:
        address_id: 地址ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        删除结果
    """
    # 查找地址
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
        Address.is_deleted == False
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地址不存在"
        )
    
    # 检查是否有关联的订单
    order_count = db.query(Order).filter(
        Order.address_id == address_id,
        Order.status.in_([0, 1, 2]),  # 进行中的订单
        Order.is_deleted == False
    ).count()
    
    if order_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该地址有进行中的订单，无法删除"
        )
    
    # 软删除
    address.is_deleted = True
    db.commit()
    
    return {"message": "地址已删除"} 