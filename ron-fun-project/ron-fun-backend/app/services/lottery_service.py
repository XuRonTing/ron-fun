import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.lottery import LotteryActivity, LotteryRecord, LotteryPrize, LotteryType
from app.models.user import User
from app.models.point import PointLog
from app.schemas.lottery import LotteryDrawRequest

logger = logging.getLogger(__name__)

class LotteryService:
    """
    抽奖服务，提供抽奖相关的功能
    """
    
    def get_activity(self, db: Session, activity_id: int) -> LotteryActivity:
        """
        获取抽奖活动
        
        Args:
            db: 数据库会话
            activity_id: 活动ID
            
        Returns:
            抽奖活动对象
            
        Raises:
            HTTPException: 如果活动不存在
        """
        activity = db.query(LotteryActivity).filter(
            LotteryActivity.id == activity_id,
            LotteryActivity.is_deleted == False
        ).first()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="抽奖活动不存在"
            )
            
        return activity
    
    def check_activity_status(self, activity: LotteryActivity) -> None:
        """
        检查抽奖活动状态
        
        Args:
            activity: 抽奖活动对象
            
        Raises:
            HTTPException: 如果活动未启用或已过期
        """
        now = datetime.now()
        
        if not activity.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="抽奖活动未启用"
            )
            
        if activity.start_time and activity.start_time > now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="抽奖活动尚未开始"
            )
            
        if activity.end_time and activity.end_time < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="抽奖活动已结束"
            )
    
    def check_draw_limits(self, db: Session, user_id: int, activity: LotteryActivity) -> None:
        """
        检查抽奖次数限制
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            activity: 抽奖活动对象
            
        Raises:
            HTTPException: 如果超出抽奖次数限制
        """
        # 检查总次数限制
        if activity.total_limit > 0:
            total_draws = db.query(func.count(LotteryRecord.id)).filter(
                LotteryRecord.user_id == user_id,
                LotteryRecord.activity_id == activity.id,
                LotteryRecord.is_deleted == False
            ).scalar()
            
            if total_draws >= activity.total_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="已达到活动总抽奖次数限制"
                )
        
        # 检查每日次数限制
        if activity.daily_limit > 0:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            daily_draws = db.query(func.count(LotteryRecord.id)).filter(
                LotteryRecord.user_id == user_id,
                LotteryRecord.activity_id == activity.id,
                LotteryRecord.created_at >= today_start,
                LotteryRecord.created_at < today_end,
                LotteryRecord.is_deleted == False
            ).scalar()
            
            if daily_draws >= activity.daily_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="已达到今日抽奖次数限制"
                )
    
    def check_points(self, user: User, activity: LotteryActivity) -> None:
        """
        检查用户积分是否足够
        
        Args:
            user: 用户对象
            activity: 抽奖活动对象
            
        Raises:
            HTTPException: 如果积分不足
        """
        if user.points < activity.points_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="积分不足"
            )
    
    def draw_lottery(self, db: Session, user: User, activity: LotteryActivity, client_info: Dict[str, str]) -> LotteryRecord:
        """
        执行抽奖
        
        Args:
            db: 数据库会话
            user: 用户对象
            activity: 抽奖活动对象
            client_info: 客户端信息
            
        Returns:
            抽奖记录对象
        """
        # 获取奖品配置
        prizes = activity.prize_settings.get("prizes", [])
        if not prizes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="活动奖品配置错误"
            )
        
        # 根据概率抽取奖品
        prize = self._random_prize(prizes)
        
        # 创建抽奖记录
        record = LotteryRecord(
            user_id=user.id,
            activity_id=activity.id,
            prize_id=prize.get("id"),
            prize_name=prize.get("name"),
            prize_type=prize.get("type"),
            prize_amount=prize.get("amount"),
            prize_image=prize.get("image"),
            is_win=prize.get("is_win", False),
            points_cost=activity.points_cost,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent")
        )
        
        # 扣除积分
        if activity.points_cost > 0:
            user.points -= activity.points_cost
            user.used_points += activity.points_cost
            
            # 创建积分记录
            point_log = PointLog(
                user_id=user.id,
                points=-activity.points_cost,
                balance=user.points,
                type="lottery",
                related_id=activity.id,
                related_type="lottery_activity",
                description=f"参与抽奖活动：{activity.title}",
                ip_address=client_info.get("ip_address")
            )
            db.add(point_log)
        
        # 如果中奖并且是积分奖励，立即发放
        if record.is_win and record.prize_type == "points" and record.prize_amount > 0:
            user.points += record.prize_amount
            user.total_points += record.prize_amount
            
            # 创建积分记录
            point_log = PointLog(
                user_id=user.id,
                points=record.prize_amount,
                balance=user.points,
                type="lottery_win",
                related_id=activity.id,
                related_type="lottery_activity",
                description=f"抽奖活动中奖：{activity.title} - {record.prize_name}",
                ip_address=client_info.get("ip_address")
            )
            db.add(point_log)
        
        # 保存记录
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return record
    
    def _random_prize(self, prizes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        根据概率随机抽取奖品
        
        Args:
            prizes: 奖品列表，每个奖品包含概率
            
        Returns:
            抽中的奖品
        """
        # 计算总概率
        total_probability = sum(prize.get("probability", 0) for prize in prizes)
        
        # 生成随机数
        rand_num = random.random() * total_probability
        
        # 根据概率选择奖品
        current_probability = 0
        for prize in prizes:
            current_probability += prize.get("probability", 0)
            if rand_num <= current_probability:
                return prize
        
        # 如果没有抽中任何奖品（理论上不应该发生），返回最后一个
        return prizes[-1]
    
    def get_user_records(self, db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[LotteryRecord]:
        """
        获取用户的抽奖记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            抽奖记录列表
        """
        return db.query(LotteryRecord).filter(
            LotteryRecord.user_id == user_id,
            LotteryRecord.is_deleted == False
        ).order_by(LotteryRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_activity_records(self, db: Session, activity_id: int, skip: int = 0, limit: int = 10) -> List[LotteryRecord]:
        """
        获取活动的抽奖记录
        
        Args:
            db: 数据库会话
            activity_id: 活动ID
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            抽奖记录列表
        """
        return db.query(LotteryRecord).filter(
            LotteryRecord.activity_id == activity_id,
            LotteryRecord.is_deleted == False
        ).order_by(LotteryRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_activities(self, db: Session, skip: int = 0, limit: int = 10, active_only: bool = False) -> List[LotteryActivity]:
        """
        获取抽奖活动列表
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            active_only: 是否只返回激活的活动
            
        Returns:
            活动列表
        """
        query = db.query(LotteryActivity).filter(LotteryActivity.is_deleted == False)
        
        if active_only:
            now = datetime.now()
            query = query.filter(
                LotteryActivity.is_active == True,
                (LotteryActivity.start_time == None) | (LotteryActivity.start_time <= now),
                (LotteryActivity.end_time == None) | (LotteryActivity.end_time >= now)
            )
            
        return query.order_by(LotteryActivity.start_time.desc()).offset(skip).limit(limit).all()


# 创建服务实例
lottery_service = LotteryService() 