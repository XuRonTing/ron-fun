from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 商品分类基础模型
class ProductCategoryBase(BaseModel):
    name: str = Field(..., description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    icon: Optional[str] = Field(None, description="分类图标")
    sort_order: int = Field(0, description="排序值")

# 创建商品分类请求
class ProductCategoryCreate(ProductCategoryBase):
    pass

# 更新商品分类请求
class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    icon: Optional[str] = Field(None, description="分类图标")
    sort_order: Optional[int] = Field(None, description="排序值")

# 商品分类响应
class ProductCategoryResponse(ProductCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 商品基础模型
class ProductBase(BaseModel):
    product_name: str = Field(..., description="商品名称")
    product_introduction: Optional[str] = Field(None, description="商品介绍")
    points_price: int = Field(..., description="积分价格")
    original_price: Optional[int] = Field(None, description="原价，单位：分")
    stock: int = Field(0, description="库存数量，0表示无限")
    category_id: Optional[int] = Field(None, description="分类ID")
    main_image: Optional[str] = Field(None, description="主图")
    product_image: Optional[str] = Field(None, description="商品图片")
    images: Optional[List[str]] = Field(None, description="商品图片列表")
    is_recommended: bool = Field(False, description="是否推荐")
    is_hot: bool = Field(False, description="是否热门")
    is_new: bool = Field(False, description="是否新品")
    sort_order: int = Field(0, description="排序值")
    exchange_rule: Optional[str] = Field(None, description="兑换规则")
    exchange_type: str = Field("virtual", description="兑换类型：virtual虚拟，physical实物")

# 创建商品请求
class ProductCreate(ProductBase):
    pass

# 更新商品请求
class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, description="商品名称")
    product_introduction: Optional[str] = Field(None, description="商品介绍")
    points_price: Optional[int] = Field(None, description="积分价格")
    original_price: Optional[int] = Field(None, description="原价，单位：分")
    stock: Optional[int] = Field(None, description="库存数量，0表示无限")
    category_id: Optional[int] = Field(None, description="分类ID")
    main_image: Optional[str] = Field(None, description="主图")
    product_image: Optional[str] = Field(None, description="商品图片")
    images: Optional[List[str]] = Field(None, description="商品图片列表")
    is_recommended: Optional[bool] = Field(None, description="是否推荐")
    is_hot: Optional[bool] = Field(None, description="是否热门")
    is_new: Optional[bool] = Field(None, description="是否新品")
    sort_order: Optional[int] = Field(None, description="排序值")
    exchange_rule: Optional[str] = Field(None, description="兑换规则")
    exchange_type: Optional[str] = Field(None, description="兑换类型：virtual虚拟，physical实物")
    status: Optional[int] = Field(None, description="状态：1正常，0下架")

# 商品响应
class ProductResponse(ProductBase):
    id: int
    category: Optional[ProductCategoryResponse] = None
    sold_count: int = 0
    status: int = 1
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 订单项基础模型
class OrderItemBase(BaseModel):
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(1, description="数量")

# 订单项响应
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    points_price: int
    quantity: int
    total_points: int
    
    class Config:
        orm_mode = True

# 创建订单请求
class OrderCreate(BaseModel):
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(1, description="数量")
    address_id: Optional[int] = Field(None, description="收货地址ID（实物商品必填）")

# 订单响应
class OrderResponse(BaseModel):
    id: int
    order_no: str
    total_points: int
    status: int
    order_type: str
    receiver_name: Optional[str]
    receiver_phone: Optional[str]
    receiver_address: Optional[str]
    express_company: Optional[str]
    express_no: Optional[str]
    express_time: Optional[datetime]
    finish_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        orm_mode = True

# 地址基础模型
class AddressBase(BaseModel):
    name: str = Field(..., description="收货人姓名")
    phone: str = Field(..., description="收货人电话")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    district: str = Field(..., description="区县")
    address: str = Field(..., description="详细地址")
    postal_code: Optional[str] = Field(None, description="邮政编码")
    is_default: bool = Field(False, description="是否为默认地址")

# 创建地址请求
class AddressCreate(AddressBase):
    pass

# 更新地址请求
class AddressUpdate(BaseModel):
    name: Optional[str] = Field(None, description="收货人姓名")
    phone: Optional[str] = Field(None, description="收货人电话")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    address: Optional[str] = Field(None, description="详细地址")
    postal_code: Optional[str] = Field(None, description="邮政编码")
    is_default: Optional[bool] = Field(None, description="是否为默认地址")

# 地址响应
class AddressResponse(AddressBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True 