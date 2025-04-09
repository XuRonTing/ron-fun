from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.banner import Banner, BannerClick
from app.models.user import User


class BannerService:
    """
    Banner服务类，提供Banner相关的业务逻辑处理
    """
    
    @staticmethod
    def get_active_banners(db: Session, position: Optional[str] = None) -> List[Banner]:
        """
        获取活跃的Banner列表
        
        Args:
            db: 数据库会话
            position: Banner位置，如果提供则只返回指定位置的Banner
            
        Returns:
            活跃的Banner列表
        """
        query = db.query(Banner).filter(
            Banner.is_active == True,
            Banner.start_time <= datetime.now(),
            or_(
                Banner.end_time.is_(None),
                Banner.end_time >= datetime.now()
            )
        )
        
        if position:
            query = query.filter(Banner.position == position)
        
        return query.order_by(Banner.sort_order).all()
    
    @staticmethod
    def record_banner_view(db: Session, banner_id: int) -> None:
        """
        记录Banner被浏览
        
        Args:
            db: 数据库会话
            banner_id: Banner ID
        """
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Banner不存在"
            )
        
        banner.view_count += 1
        db.commit()
    
    @staticmethod
    def record_banner_click(
        db: Session, 
        banner_id: int, 
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_type: Optional[str] = None
    ) -> BannerClick:
        """
        记录Banner被点击
        
        Args:
            db: 数据库会话
            banner_id: Banner ID
            user_id: 用户ID，可选
            ip_address: IP地址，可选
            user_agent: 用户代理，可选
            device_type: 设备类型，可选
            
        Returns:
            创建的BannerClick记录
        """
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Banner不存在"
            )
        
        # 检查用户是否存在
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user_id = None
        
        # 记录点击
        banner_click = BannerClick(
            banner_id=banner_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type
        )
        
        db.add(banner_click)
        
        # 更新Banner点击数
        banner.click_count += 1
        
        db.commit()
        db.refresh(banner_click)
        
        return banner_click
    
    @staticmethod
    def get_banner_statistics(db: Session, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取Banner点击统计
        
        Args:
            db: 数据库会话
            days: 统计的天数，默认为7天
            
        Returns:
            Banner点击统计数据列表
        """
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 查询每个Banner每天的点击次数
        result = db.query(
            BannerClick.banner_id,
            func.date(BannerClick.created_at).label("date"),
            func.count().label("count")
        ).filter(
            BannerClick.created_at.between(start_date, end_date)
        ).group_by(
            BannerClick.banner_id,
            func.date(BannerClick.created_at)
        ).all()
        
        # 查询所有Banner信息以获取标题
        banners = {banner.id: banner.title for banner in db.query(Banner.id, Banner.title).all()}
        
        # 构建响应数据
        statistics = [
            {
                "banner_id": item.banner_id,
                "banner_title": banners.get(item.banner_id, "未知Banner"),
                "date": item.date.strftime("%Y-%m-%d"),
                "count": item.count
            }
            for item in result
        ]
        
        return statistics
    
    @staticmethod
    def get_banner_traffic_by_device(db: Session, days: int = 7) -> Dict[str, int]:
        """
        获取Banner点击设备分布
        
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
            BannerClick.device_type,
            func.count().label("count")
        ).filter(
            BannerClick.created_at.between(start_date, end_date)
        ).group_by(
            BannerClick.device_type
        ).all()
        
        # 构建响应数据
        statistics = {
            item.device_type or "unknown": item.count
            for item in result
        }
        
        return statistics 