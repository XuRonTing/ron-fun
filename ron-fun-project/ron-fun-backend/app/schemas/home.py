from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Banner基础模型
class BannerBase(BaseModel):
    title: str = Field(..., description="标题")
    description: Optional[str] = Field(None, description="描述")
    image: str = Field(..., description="图片URL")
    link_type: str = Field(..., description="链接类型：url, product, activity等")
    link_url: Optional[str] = Field(None, description="链接URL")
    link_id: Optional[int] = Field(None, description="关联ID")
    is_active: bool = Field(True, description="是否激活")
    sort_order: int = Field(0, description="排序值")
    position: str = Field("home", description="展示位置：home首页, mall商城等")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")

# 创建Banner请求
class BannerCreate(BannerBase):
    pass

# 更新Banner请求
class BannerUpdate(BaseModel):
    title: Optional[str] = Field(None, description="标题")
    description: Optional[str] = Field(None, description="描述")
    image: Optional[str] = Field(None, description="图片URL")
    link_type: Optional[str] = Field(None, description="链接类型：url, product, activity等")
    link_url: Optional[str] = Field(None, description="链接URL")
    link_id: Optional[int] = Field(None, description="关联ID")
    is_active: Optional[bool] = Field(None, description="是否激活")
    sort_order: Optional[int] = Field(None, description="排序值")
    position: Optional[str] = Field(None, description="展示位置：home首页, mall商城等")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")

# Banner响应
class BannerResponse(BannerBase):
    id: int
    view_count: int = 0
    click_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 应用基础模型
class ApplicationBase(BaseModel):
    app_name: str = Field(..., description="应用名称")
    app_introduction: Optional[str] = Field(None, description="应用介绍")
    app_icon: Optional[str] = Field(None, description="应用图标")
    app_link: str = Field(..., description="应用链接")
    link_type: str = Field(..., description="链接类型：url, internal等")
    link_url: Optional[str] = Field(None, description="链接URL")
    is_active: bool = Field(True, description="是否激活")
    sort_order: int = Field(0, description="排序值")
    position: str = Field("home", description="展示位置：home首页, sidebar侧边栏等")

# 创建应用请求
class ApplicationCreate(ApplicationBase):
    pass

# 更新应用请求
class ApplicationUpdate(BaseModel):
    app_name: Optional[str] = Field(None, description="应用名称")
    app_introduction: Optional[str] = Field(None, description="应用介绍")
    app_icon: Optional[str] = Field(None, description="应用图标")
    app_link: Optional[str] = Field(None, description="应用链接")
    link_type: Optional[str] = Field(None, description="链接类型：url, internal等")
    link_url: Optional[str] = Field(None, description="链接URL")
    is_active: Optional[bool] = Field(None, description="是否激活")
    sort_order: Optional[int] = Field(None, description="排序值")
    position: Optional[str] = Field(None, description="展示位置：home首页, sidebar侧边栏等")

# 应用响应
class ApplicationResponse(ApplicationBase):
    id: int
    view_count: int = 0
    click_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 首页数据响应
class HomeDataResponse(BaseModel):
    banners: List[BannerResponse]
    applications: List[ApplicationResponse] 