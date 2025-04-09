from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_active_superuser, get_current_user, get_optional_current_user
from app.models.user import User
from app.models.banner import Banner
from app.schemas.banner import BannerResponse, BannerCreate, BannerUpdate
from app.schemas.common import ApiResponse
from app.services.banner_service import BannerService

router = APIRouter()

@router.get("/", response_model=List[BannerResponse])
async def get_banners(
    db: Session = Depends(get_db),
    position: Optional[str] = None,
    include_inactive: bool = False
):
    """获取Banner列表"""
    if include_inactive:
        query = db.query(Banner)
        if position:
            query = query.filter(Banner.position == position)
        banners = query.order_by(Banner.sort_order).all()
    else:
        banners = BannerService.get_active_banners(db, position)
    
    return banners

@router.get("/{banner_id}", response_model=BannerResponse)
async def get_banner(
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """获取Banner详情"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner不存在"
        )
    return banner

@router.post("/", response_model=BannerResponse, status_code=status.HTTP_201_CREATED)
async def create_banner(
    banner_create: BannerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """创建Banner（仅管理员）"""
    banner = Banner(**banner_create.dict())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return banner

@router.put("/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_update: BannerUpdate,
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """更新Banner（仅管理员）"""
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

@router.delete("/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_banner(
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """删除Banner（仅管理员）"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner不存在"
        )
    
    # 标记为删除（软删除）
    banner.is_active = False
    banner.deleted_at = datetime.now()
    
    db.commit()
    
    return None

@router.post("/{banner_id}/view", response_model=ApiResponse)
async def record_banner_view(
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """记录Banner被浏览"""
    try:
        BannerService.record_banner_view(db, banner_id)
        return {"code": 200, "message": "success", "data": None}
    except HTTPException as e:
        return {"code": e.status_code, "message": e.detail, "data": None}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}

@router.post("/{banner_id}/click", response_model=ApiResponse)
async def record_banner_click(
    request: Request,
    banner_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """记录Banner被点击"""
    try:
        # 获取请求信息
        user_id = current_user.id if current_user else None
        ip_address = request.client.host if hasattr(request.client, "host") else None
        user_agent = request.headers.get("user-agent")
        
        # 根据User-Agent判断设备类型（简化版）
        device_type = "unknown"
        if user_agent:
            user_agent_lower = user_agent.lower()
            if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
                device_type = "mobile"
            elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
                device_type = "tablet"
            else:
                device_type = "desktop"
        
        # 记录点击
        BannerService.record_banner_click(
            db, 
            banner_id, 
            user_id=user_id, 
            ip_address=ip_address, 
            user_agent=user_agent, 
            device_type=device_type
        )
        
        return {"code": 200, "message": "success", "data": None}
    except HTTPException as e:
        return {"code": e.status_code, "message": e.detail, "data": None}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None} 