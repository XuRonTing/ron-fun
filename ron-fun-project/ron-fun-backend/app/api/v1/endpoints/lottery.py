from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_active_superuser
from app.models.user import User
from app.models.lottery import LotteryActivity, LotteryType, LotteryRecord, LotteryPrize
from app.schemas.lottery import (
    LotteryActivityCreate, LotteryActivityUpdate, LotteryActivityResponse,
    LotteryTypeCreate, LotteryTypeUpdate, LotteryTypeResponse,
    LotteryPrizeCreate, LotteryPrizeUpdate, LotteryPrizeResponse,
    LotteryRecordResponse, LotteryDrawRequest
)
from app.services.lottery_service import lottery_service

router = APIRouter()

# 抽奖类型相关接口
@router.post("/types", response_model=LotteryTypeResponse, summary="创建抽奖类型")
async def create_lottery_type(
    lottery_type_in: LotteryTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    创建抽奖类型（仅限管理员）
    
    Args:
        lottery_type_in: 抽奖类型创建请求
        db: 数据库会话
        current_user: 当前用户(管理员)
        
    Returns:
        创建的抽奖类型
    """
    # 检查代码是否已存在
    existing_type = db.query(LotteryType).filter(LotteryType.code == lottery_type_in.code).first()
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="抽奖类型代码已存在"
        )
    
    # 创建抽奖类型
    lottery_type = LotteryType(**lottery_type_in.dict())
    db.add(lottery_type)
    db.commit()
    db.refresh(lottery_type)
    
    return lottery_type

@router.get("/types", response_model=List[LotteryTypeResponse], summary="获取抽奖类型列表")
async def get_lottery_types(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取抽奖类型列表
    
    Args:
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        抽奖类型列表
    """
    lottery_types = db.query(LotteryType).filter(LotteryType.is_deleted == False).offset(skip).limit(limit).all()
    return lottery_types

@router.get("/types/{type_id}", response_model=LotteryTypeResponse, summary="获取抽奖类型详情")
async def get_lottery_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取抽奖类型详情
    
    Args:
        type_id: 抽奖类型ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        抽奖类型详情
    """
    lottery_type = db.query(LotteryType).filter(
        LotteryType.id == type_id,
        LotteryType.is_deleted == False
    ).first()
    
    if not lottery_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="抽奖类型不存在"
        )
    
    return lottery_type

@router.put("/types/{type_id}", response_model=LotteryTypeResponse, summary="更新抽奖类型")
async def update_lottery_type(
    type_id: int,
    lottery_type_in: LotteryTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    更新抽奖类型（仅限管理员）
    
    Args:
        type_id: 抽奖类型ID
        lottery_type_in: 抽奖类型更新请求
        db: 数据库会话
        current_user: 当前用户(管理员)
        
    Returns:
        更新后的抽奖类型
    """
    lottery_type = db.query(LotteryType).filter(
        LotteryType.id == type_id,
        LotteryType.is_deleted == False
    ).first()
    
    if not lottery_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="抽奖类型不存在"
        )
    
    # 更新字段
    update_data = lottery_type_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lottery_type, field, value)
    
    db.commit()
    db.refresh(lottery_type)
    
    return lottery_type

@router.delete("/types/{type_id}", summary="删除抽奖类型")
async def delete_lottery_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    删除抽奖类型（仅限管理员）
    
    Args:
        type_id: 抽奖类型ID
        db: 数据库会话
        current_user: 当前用户(管理员)
        
    Returns:
        删除结果
    """
    lottery_type = db.query(LotteryType).filter(
        LotteryType.id == type_id,
        LotteryType.is_deleted == False
    ).first()
    
    if not lottery_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="抽奖类型不存在"
        )
    
    # 检查是否有关联的活动
    activity_count = db.query(LotteryActivity).filter(
        LotteryActivity.lottery_type_id == type_id,
        LotteryActivity.is_deleted == False
    ).count()
    
    if activity_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该抽奖类型下存在活动，无法删除"
        )
    
    # 软删除
    lottery_type.is_deleted = True
    db.commit()
    
    return {"message": "抽奖类型已删除"}

# 抽奖活动相关接口
@router.post("/activities", response_model=LotteryActivityResponse, summary="创建抽奖活动")
async def create_lottery_activity(
    activity_in: LotteryActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    创建抽奖活动（仅限管理员）
    
    Args:
        activity_in: 抽奖活动创建请求
        db: 数据库会话
        current_user: 当前用户(管理员)
        
    Returns:
        创建的抽奖活动
    """
    # 检查抽奖类型是否存在
    lottery_type = db.query(LotteryType).filter(
        LotteryType.id == activity_in.lottery_type_id,
        LotteryType.is_deleted == False
    ).first()
    
    if not lottery_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="抽奖类型不存在"
        )
    
    # 创建抽奖活动
    activity = LotteryActivity(**activity_in.dict())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return activity

@router.get("/activities", response_model=List[LotteryActivityResponse], summary="获取抽奖活动列表")
async def get_lottery_activities(
    skip: int = 0,
    limit: int = 10,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取抽奖活动列表
    
    Args:
        skip: 跳过记录数
        limit: 返回记录数
        active_only: 是否只返回激活的活动
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        抽奖活动列表
    """
    activities = lottery_service.get_activities(db, skip, limit, active_only)
    return activities

@router.get("/activities/{activity_id}", response_model=LotteryActivityResponse, summary="获取抽奖活动详情")
async def get_lottery_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取抽奖活动详情
    
    Args:
        activity_id: 抽奖活动ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        抽奖活动详情
    """
    activity = lottery_service.get_activity(db, activity_id)
    return activity

@router.put("/activities/{activity_id}", response_model=LotteryActivityResponse, summary="更新抽奖活动")
async def update_lottery_activity(
    activity_id: int,
    activity_in: LotteryActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    更新抽奖活动（仅限管理员）
    
    Args:
        activity_id: 抽奖活动ID
        activity_in: 抽奖活动更新请求
        db: 数据库会话
        current_user: 当前用户(管理员)
        
    Returns:
        更新后的抽奖活动
    """
    activity = lottery_service.get_activity(db, activity_id)
    
    # 更新字段
    update_data = activity_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    db.commit()
    db.refresh(activity)
    
    return activity

@router.delete("/activities/{activity_id}", summary="删除抽奖活动")
async def delete_lottery_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    删除抽奖活动（仅限管理员）
    
    Args:
        activity_id: 抽奖活动ID
        db: 数据库会话
        current_user: 当前用户(管理员)
        
    Returns:
        删除结果
    """
    activity = lottery_service.get_activity(db, activity_id)
    
    # 检查是否有抽奖记录
    record_count = db.query(LotteryRecord).filter(
        LotteryRecord.activity_id == activity_id,
        LotteryRecord.is_deleted == False
    ).count()
    
    if record_count > 0:
        # 如果有记录，则只禁用活动而不删除
        activity.is_active = False
        db.commit()
        return {"message": "抽奖活动已禁用（存在抽奖记录，无法彻底删除）"}
    
    # 否则软删除
    activity.is_deleted = True
    db.commit()
    
    return {"message": "抽奖活动已删除"}

@router.post("/draw", response_model=LotteryRecordResponse, summary="执行抽奖")
async def draw_lottery(
    draw_request: LotteryDrawRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    执行抽奖
    
    Args:
        draw_request: 抽奖请求
        request: 请求对象
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        抽奖结果
    """
    # 获取活动
    activity = lottery_service.get_activity(db, draw_request.activity_id)
    
    # 检查活动状态
    lottery_service.check_activity_status(activity)
    
    # 检查抽奖次数限制
    lottery_service.check_draw_limits(db, current_user.id, activity)
    
    # 检查积分是否足够
    lottery_service.check_points(current_user, activity)
    
    # 获取客户端信息
    client_info = {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }
    
    # 执行抽奖
    record = lottery_service.draw_lottery(db, current_user, activity, client_info)
    
    return record

@router.get("/records", response_model=List[LotteryRecordResponse], summary="获取抽奖记录")
async def get_lottery_records(
    activity_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取抽奖记录
    
    Args:
        activity_id: 活动ID，不提供则获取当前用户的所有记录
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        抽奖记录列表
    """
    if activity_id:
        # 如果是管理员，可以查看活动的所有记录
        if current_user.is_superuser:
            records = lottery_service.get_activity_records(db, activity_id, skip, limit)
        else:
            # 否则只能查看自己在该活动中的记录
            records = db.query(LotteryRecord).filter(
                LotteryRecord.activity_id == activity_id,
                LotteryRecord.user_id == current_user.id,
                LotteryRecord.is_deleted == False
            ).order_by(LotteryRecord.created_at.desc()).offset(skip).limit(limit).all()
    else:
        # 获取用户的所有记录
        records = lottery_service.get_user_records(db, current_user.id, skip, limit)
    
    return records 