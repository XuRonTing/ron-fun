from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_active_superuser, get_current_user, get_optional_current_user
from app.models.user import User
from app.models.application import Application
from app.schemas.application import ApplicationResponse, ApplicationCreate, ApplicationUpdate
from app.schemas.common import ApiResponse
from app.services.application_service import ApplicationService

router = APIRouter()

@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    db: Session = Depends(get_db),
    position: Optional[str] = None,
    include_inactive: bool = False
):
    """获取应用列表"""
    if include_inactive:
        query = db.query(Application)
        if position:
            query = query.filter(Application.position == position)
        applications = query.order_by(Application.sort_order).all()
    else:
        applications = ApplicationService.get_active_applications(db, position)
    
    return applications

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """获取应用详情"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="应用不存在"
        )
    return application

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_create: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """创建应用（仅管理员）"""
    application = Application(**application_create.dict())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_update: ApplicationUpdate,
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """更新应用（仅管理员）"""
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

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """删除应用（仅管理员）"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="应用不存在"
        )
    
    # 标记为删除（软删除）
    application.is_active = False
    application.deleted_at = datetime.now()
    
    db.commit()
    
    return None

@router.post("/{application_id}/view", response_model=ApiResponse)
async def record_application_view(
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """记录应用被浏览"""
    try:
        ApplicationService.record_application_view(db, application_id)
        return {"code": 200, "message": "success", "data": None}
    except HTTPException as e:
        return {"code": e.status_code, "message": e.detail, "data": None}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": None}

@router.post("/{application_id}/click", response_model=ApiResponse)
async def record_application_click(
    request: Request,
    application_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """记录应用被点击"""
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
        ApplicationService.record_application_click(
            db, 
            application_id, 
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