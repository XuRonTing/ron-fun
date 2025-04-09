import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.banner import Banner, BannerClick
from app.models.application import Application, ApplicationClick
from app.models.user import User

logger = logging.getLogger(__name__)

class HomeService:
    """
    首页服务，提供Banner和Application相关功能
    """
    
    def get_banners(
        self, 
        db: Session, 
        position: str = "home", 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Banner]:
        """
        获取Banner列表
        
        Args:
            db: 数据库会话
            position: 展示位置
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            Banner列表
        """
        now = datetime.now()
        
        banners = db.query(Banner).filter(
            Banner.is_deleted == False,
            Banner.is_active == True,
            Banner.position == position,
            (Banner.start_time == None) | (Banner.start_time <= now),
            (Banner.end_time == None) | (Banner.end_time >= now)
        ).order_by(
            Banner.sort_order.desc()
        ).offset(skip).limit(limit).all()
        
        return banners
    
    def get_banner(self, db: Session, banner_id: int) -> Banner:
        """
        获取Banner详情
        
        Args:
            db: 数据库会话
            banner_id: Banner ID
            
        Returns:
            Banner对象
            
        Raises:
            HTTPException: 如果Banner不存在
        """
        banner = db.query(Banner).filter(
            Banner.id == banner_id,
            Banner.is_deleted == False
        ).first()
        
        if not banner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Banner不存在"
            )
            
        return banner
    
    def record_banner_click(
        self, 
        db: Session, 
        banner_id: int, 
        user: Optional[User] = None,
        request: Optional[Request] = None
    ) -> None:
        """
        记录Banner点击
        
        Args:
            db: 数据库会话
            banner_id: Banner ID
            user: 用户对象（可选）
            request: 请求对象（用于获取IP和UA）
        """
        # 获取Banner
        banner = self.get_banner(db, banner_id)
        
        # 增加点击次数
        banner.click_count += 1
        
        # 创建点击记录
        click = BannerClick(
            banner_id=banner_id,
            user_id=user.id if user else None,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            device_type=self._get_device_type(request) if request else None
        )
        
        db.add(click)
        db.commit()
    
    def get_applications(
        self, 
        db: Session, 
        position: str = "home", 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Application]:
        """
        获取应用列表
        
        Args:
            db: 数据库会话
            position: 展示位置
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            应用列表
        """
        applications = db.query(Application).filter(
            Application.is_deleted == False,
            Application.is_active == True,
            Application.position == position
        ).order_by(
            Application.sort_order.desc()
        ).offset(skip).limit(limit).all()
        
        return applications
    
    def get_application(self, db: Session, app_id: int) -> Application:
        """
        获取应用详情
        
        Args:
            db: 数据库会话
            app_id: 应用ID
            
        Returns:
            应用对象
            
        Raises:
            HTTPException: 如果应用不存在
        """
        application = db.query(Application).filter(
            Application.id == app_id,
            Application.is_deleted == False
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="应用不存在"
            )
            
        return application
    
    def record_application_click(
        self, 
        db: Session, 
        app_id: int, 
        user: Optional[User] = None,
        request: Optional[Request] = None
    ) -> None:
        """
        记录应用点击
        
        Args:
            db: 数据库会话
            app_id: 应用ID
            user: 用户对象（可选）
            request: 请求对象（用于获取IP和UA）
        """
        # 获取应用
        application = self.get_application(db, app_id)
        
        # 增加点击次数
        application.click_count += 1
        
        # 创建点击记录
        click = ApplicationClick(
            application_id=app_id,
            user_id=user.id if user else None,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            device_type=self._get_device_type(request) if request else None
        )
        
        db.add(click)
        db.commit()
    
    def _get_device_type(self, request: Request) -> str:
        """
        根据User-Agent判断设备类型
        
        Args:
            request: 请求对象
            
        Returns:
            设备类型：mobile, desktop等
        """
        user_agent = request.headers.get("user-agent", "").lower()
        
        if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent or "ipad" in user_agent:
            return "mobile"
        else:
            return "desktop"

# 创建服务实例
home_service = HomeService() 