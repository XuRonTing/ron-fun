import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.product import Product, ProductCategory, Order, OrderItem, Address
from app.models.user import User
from app.models.point import PointLog

logger = logging.getLogger(__name__)

class ProductService:
    """
    商品服务，提供商品管理相关功能
    """
    
    def get_product(self, db: Session, product_id: int) -> Product:
        """
        获取商品详情
        
        Args:
            db: 数据库会话
            product_id: 商品ID
            
        Returns:
            商品对象
            
        Raises:
            HTTPException: 如果商品不存在
        """
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_deleted == False,
            Product.status == 1  # 正常状态
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品不存在"
            )
            
        return product
    
    def get_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 10, 
        category_id: Optional[int] = None,
        is_recommended: Optional[bool] = None,
        is_hot: Optional[bool] = None,
        is_new: Optional[bool] = None,
        keyword: Optional[str] = None
    ) -> List[Product]:
        """
        获取商品列表
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            category_id: 分类ID
            is_recommended: 是否推荐
            is_hot: 是否热门
            is_new: 是否新品
            keyword: 搜索关键词
            
        Returns:
            商品列表
        """
        query = db.query(Product).filter(
            Product.is_deleted == False,
            Product.status == 1  # 正常状态
        )
        
        # 按分类筛选
        if category_id:
            query = query.filter(Product.category_id == category_id)
            
        # 按属性筛选
        if is_recommended is not None:
            query = query.filter(Product.is_recommended == is_recommended)
            
        if is_hot is not None:
            query = query.filter(Product.is_hot == is_hot)
            
        if is_new is not None:
            query = query.filter(Product.is_new == is_new)
            
        # 按关键词搜索
        if keyword:
            query = query.filter(
                Product.product_name.ilike(f"%{keyword}%") | 
                Product.product_introduction.ilike(f"%{keyword}%")
            )
            
        # 排序
        query = query.order_by(desc(Product.sort_order), desc(Product.created_at))
        
        # 分页
        products = query.offset(skip).limit(limit).all()
        
        return products
    
    def get_categories(self, db: Session, skip: int = 0, limit: int = 10) -> List[ProductCategory]:
        """
        获取商品分类列表
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            分类列表
        """
        categories = db.query(ProductCategory).filter(
            ProductCategory.is_deleted == False
        ).order_by(
            ProductCategory.sort_order.desc()
        ).offset(skip).limit(limit).all()
        
        return categories
    
    def create_order(
        self, 
        db: Session, 
        user: User, 
        product_id: int, 
        quantity: int = 1,
        address_id: Optional[int] = None,
        client_info: Dict[str, str] = None
    ) -> Order:
        """
        创建订单
        
        Args:
            db: 数据库会话
            user: 用户对象
            product_id: 商品ID
            quantity: 数量
            address_id: 收货地址ID（实物商品必填）
            client_info: 客户端信息
            
        Returns:
            订单对象
        """
        # 获取商品
        product = self.get_product(db, product_id)
        
        # 检查库存
        if product.stock > 0 and product.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="商品库存不足"
            )
        
        # 计算总积分
        total_points = product.points_price * quantity
        
        # 检查积分是否足够
        if user.points < total_points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="积分不足"
            )
        
        # 如果是实物商品，检查收货地址
        if product.exchange_type == "physical" and not address_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请提供收货地址"
            )
        
        # 生成订单号（简单实现，实际应更复杂）
        order_no = f"ORDER{datetime.now().strftime('%Y%m%d%H%M%S')}{user.id}"
        
        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user.id,
            total_points=total_points,
            order_type="points",
            status=0  # 待处理
        )
        
        # 如果有收货地址，添加地址信息
        if address_id:
            address = db.query(Address).filter(
                Address.id == address_id,
                Address.user_id == user.id,
                Address.is_deleted == False
            ).first()
            
            if not address:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="收货地址不存在"
                )
            
            order.address_id = address.id
            order.receiver_name = address.name
            order.receiver_phone = address.phone
            order.receiver_address = f"{address.province}{address.city}{address.district}{address.address}"
        
        # 保存订单
        db.add(order)
        db.flush()  # 获取ID但不提交事务
        
        # 创建订单项
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.product_name,
            product_image=product.main_image or product.product_image,
            points_price=product.points_price,
            quantity=quantity,
            total_points=total_points
        )
        
        # 保存订单项
        db.add(order_item)
        
        # 扣除积分
        user.points -= total_points
        user.used_points += total_points
        
        # 创建积分记录
        point_log = PointLog(
            user_id=user.id,
            points=-total_points,
            balance=user.points,
            type="exchange",
            related_id=order.id,
            related_type="order",
            description=f"兑换商品：{product.product_name}",
            ip_address=client_info.get("ip_address") if client_info else None
        )
        db.add(point_log)
        
        # 减少库存，增加销量
        if product.stock > 0:
            product.stock -= quantity
        product.sold_count += quantity
        
        # 如果是虚拟商品，自动完成订单
        if product.exchange_type == "virtual":
            order.status = 3  # 已完成
            order.finish_time = datetime.now()
        
        # 提交事务
        db.commit()
        db.refresh(order)
        
        return order
    
    def get_user_orders(
        self, 
        db: Session, 
        user_id: int, 
        status: Optional[int] = None,
        skip: int = 0, 
        limit: int = 10
    ) -> List[Order]:
        """
        获取用户订单列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 订单状态
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            订单列表
        """
        query = db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_deleted == False
        )
        
        # 按状态筛选
        if status is not None:
            query = query.filter(Order.status == status)
            
        # 排序和分页
        orders = query.order_by(
            Order.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return orders

# 创建服务实例
product_service = ProductService() 