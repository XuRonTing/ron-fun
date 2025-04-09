from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.application import Application, ApplicationClick
from app.models.user import User


class ApplicationService:
    """
    应用服务类，提供应用相关的业务逻辑处理
    """
    
    @staticmethod
    def get_active_applications(db: Session, position: Optional[str] = None) -> List[Application]:
        """
        获取活跃的应用列表
        
        Args:
            db: 数据库会话
            position: 应用位置，如果提供则只返回指定位置的应用
            
        Returns:
            活跃的应用列表
        """
        query = db.query(Application).filter(Application.is_active == True)
        
        if position:
            query = query.filter(Application.position == position)
        
        return query.order_by(Application.sort_order).all()
    
    @staticmethod
    def record_application_view(db: Session, application_id: int) -> None:
        """
        记录应用被浏览
        
        Args:
            db: 数据库会话
            application_id: 应用ID
        """
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="应用不存在"
            )
        
        application.view_count += 1
        db.commit()
    
    @staticmethod
    def record_application_click(
        db: Session, 
        application_id: int, 
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_type: Optional[str] = None
    ) -> ApplicationClick:
        """
        记录应用被点击
        
        Args:
            db: 数据库会话
            application_id: 应用ID
            user_id: 用户ID，可选
            ip_address: IP地址，可选
            user_agent: 用户代理，可选
            device_type: 设备类型，可选
            
        Returns:
            创建的ApplicationClick记录
        """
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="应用不存在"
            )
        
        # 检查用户是否存在
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user_id = None
        
        # 记录点击
        application_click = ApplicationClick(
            application_id=application_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type
        )
        
        db.add(application_click)
        
        # 更新应用点击数
        application.click_count += 1
        
        db.commit()
        db.refresh(application_click)
        
        return application_click
    
    @staticmethod
    def get_application_statistics(db: Session, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取应用点击统计
        
        Args:
            db: 数据库会话
            days: 统计的天数，默认为7天
            
        Returns:
            应用点击统计数据列表
        """
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 查询每个应用每天的点击次数
        result = db.query(
            ApplicationClick.application_id,
            func.date(ApplicationClick.created_at).label("date"),
            func.count().label("count")
        ).filter(
            ApplicationClick.created_at.between(start_date, end_date)
        ).group_by(
            ApplicationClick.application_id,
            func.date(ApplicationClick.created_at)
        ).all()
        
        # 查询所有应用信息以获取名称
        applications = {app.id: app.name for app in db.query(Application.id, Application.name).all()}
        
        # 构建响应数据
        statistics = [
            {
                "application_id": item.application_id,
                "application_name": applications.get(item.application_id, "未知应用"),
                "date": item.date.strftime("%Y-%m-%d"),
                "count": item.count
            }
            for item in result
        ]
        
        return statistics
    
    @staticmethod
    def get_application_traffic_by_device(db: Session, days: int = 7) -> Dict[str, int]:
        """
        获取应用点击设备分布
        
        Args:
            db: 数据库会话
            days: 统计的天数，默认为7天
            
        Returns:
            不同设备类型的点击次数字典
        """
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 查询不同设备类型的点击次数
        result = db.query(
            ApplicationClick.device_type,
            func.count().label("count")
        ).filter(
            ApplicationClick.created_at.between(start_date, end_date)
        ).group_by(
            ApplicationClick.device_type
        ).all()
        
        # 构建响应数据
        statistics = {
            item.device_type or "unknown": item.count
            for item in result
        }
        
        return statistics 