from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.session import Base
from app.models.base import Base as CustomBase

class Product(Base, CustomBase):
    """
    商品模型
    """
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False, index=True)
    product_introduction = Column(String(500), nullable=True)
    product_price = Column(Integer, nullable=False)  # 积分价格
    product_stock = Column(Integer, nullable=False, default=0)
    product_ordering = Column(Integer, nullable=False, default=0)  # 排序权重
    product_is_on_sale = Column(Boolean, nullable=False, default=True)  # 是否上架
    product_image = Column(String(255), nullable=True)  # 商品图片
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # 关联关系
    point_records = relationship("PointRecord", back_populates="product")
    orders = relationship("Order", back_populates="product")

    # 分类
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True, comment="分类ID")
    category = relationship("ProductCategory", back_populates="products")
    
    # 价格和库存
    points_price = Column(Integer, nullable=False, comment="积分价格")
    original_price = Column(Integer, nullable=True, comment="原价，单位：分")
    stock = Column(Integer, default=0, comment="库存数量，0表示无限")
    sold_count = Column(Integer, default=0, comment="已售数量")
    
    # 图片
    main_image = Column(String(255), nullable=True, comment="主图")
    images = Column(JSON, nullable=True, comment="商品图片列表")
    
    # 商品状态
    status = Column(Integer, default=1, comment="状态：1正常，0下架")
    is_recommended = Column(Boolean, default=False, comment="是否推荐")
    is_hot = Column(Boolean, default=False, comment="是否热门")
    is_new = Column(Boolean, default=False, comment="是否新品")
    
    # 排序
    sort_order = Column(Integer, default=0, comment="排序值，数值越大越靠前")
    
    # 兑换规则
    exchange_rule = Column(Text, nullable=True, comment="兑换规则")
    exchange_type = Column(String(50), default="virtual", comment="兑换类型：virtual虚拟，physical实物")

class ProductCategory(Base, CustomBase):
    """
    商品分类模型
    """
    name = Column(String(50), nullable=False, comment="分类名称")
    description = Column(Text, nullable=True, comment="分类描述")
    icon = Column(String(255), nullable=True, comment="分类图标")
    
    # 排序
    sort_order = Column(Integer, default=0, comment="排序值")
    
    # 关联
    products = relationship("Product", back_populates="category")

class Order(Base, CustomBase):
    """
    订单模型
    """
    # 订单基本信息
    order_no = Column(String(50), unique=True, nullable=False, comment="订单号")
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    user = relationship("User", back_populates="orders", foreign_keys=[user_id])
    
    # 订单金额
    total_points = Column(Integer, nullable=False, comment="总积分")
    total_amount = Column(Integer, default=0, comment="总金额（如有）")
    
    # 订单状态
    status = Column(Integer, default=0, comment="状态：0待处理，1已确认，2已发货，3已完成，-1已取消")
    
    # 订单类型
    order_type = Column(String(50), default="points", comment="订单类型：points积分兑换，mixed混合支付")
    
    # 收货信息
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=True, comment="收货地址ID")
    address = relationship("Address", back_populates="orders")
    
    receiver_name = Column(String(50), nullable=True, comment="收货人姓名")
    receiver_phone = Column(String(20), nullable=True, comment="收货人电话")
    receiver_address = Column(String(255), nullable=True, comment="收货地址")
    
    # 物流信息
    express_company = Column(String(50), nullable=True, comment="快递公司")
    express_no = Column(String(50), nullable=True, comment="快递单号")
    express_time = Column(DateTime, nullable=True, comment="发货时间")
    
    # 完成时间
    finish_time = Column(DateTime, nullable=True, comment="完成时间")
    
    # 取消信息
    cancel_time = Column(DateTime, nullable=True, comment="取消时间")
    cancel_reason = Column(String(255), nullable=True, comment="取消原因")
    
    # 备注
    remark = Column(String(255), nullable=True, comment="订单备注")
    
    # 关联
    items = relationship("OrderItem", back_populates="order")
    
    # 操作人（管理员操作时）
    operator_id = Column(Integer, nullable=True, comment="操作人ID")
    operator_name = Column(String(50), nullable=True, comment="操作人姓名")

class OrderItem(Base, CustomBase):
    """
    订单项模型
    """
    # 关联订单
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    order = relationship("Order", back_populates="items")
    
    # 关联商品
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")
    product = relationship("Product", back_populates="orders")
    
    # 商品信息快照
    product_name = Column(String(100), nullable=False, comment="商品名称")
    product_image = Column(String(255), nullable=True, comment="商品图片")
    points_price = Column(Integer, nullable=False, comment="积分价格")
    
    # 数量和总价
    quantity = Column(Integer, default=1, comment="数量")
    total_points = Column(Integer, nullable=False, comment="总积分")

class Address(Base, CustomBase):
    """
    收货地址模型
    """
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    user = relationship("User", back_populates="addresses")
    
    # 收货信息
    name = Column(String(50), nullable=False, comment="收货人姓名")
    phone = Column(String(20), nullable=False, comment="收货人电话")
    province = Column(String(50), nullable=False, comment="省份")
    city = Column(String(50), nullable=False, comment="城市")
    district = Column(String(50), nullable=False, comment="区县")
    address = Column(String(255), nullable=False, comment="详细地址")
    postal_code = Column(String(20), nullable=True, comment="邮政编码")
    
    # 默认地址
    is_default = Column(Boolean, default=False, comment="是否为默认地址")
    
    # 关联
    orders = relationship("Order", back_populates="address") 