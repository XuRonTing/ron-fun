from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from datetime import datetime

# 泛型类型
T = TypeVar('T')

# 分页请求参数
class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10
    sort: Optional[str] = None
    order: Optional[str] = None  # asc, desc

# 分页响应数据
class PaginationData(GenericModel, Generic[T]):
    list: List[T]
    total: int
    page: int
    size: int
    pages: int
    
# API通用响应格式
class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: int = 0  # 时间戳，由中间件自动填充 

class PaginatedResponse(BaseModel, Generic[T]):
    """
    通用分页响应模型
    
    泛型参数T代表分页项目的类型
    """
    items: List[T]
    total: int = Field(..., description="总条目数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页条目数")

class DateRangeParams(BaseModel):
    """
    日期范围查询参数
    """
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")

class IdResponse(BaseModel):
    """
    ID响应模型，通常用于创建操作
    """
    id: int = Field(..., description="创建的资源ID") 