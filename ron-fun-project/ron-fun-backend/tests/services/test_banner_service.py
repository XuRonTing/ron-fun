import pytest
from datetime import datetime, timedelta

from app.services.banner_service import BannerService
from app.models.banner import Banner, BannerClick

def test_get_active_banners(db, create_test_banners):
    """测试获取活跃Banner列表"""
    # 创建一个已过期的Banner
    expired_banner = Banner(
        title="Expired Banner",
        description="This banner has expired",
        image_url="http://example.com/expired_banner.jpg",
        link_type="url",
        link_url="http://example.com/expired",
        is_active=True,
        sort_order=100,
        position="home_top",
        start_time=datetime.now() - timedelta(days=10),
        end_time=datetime.now() - timedelta(days=1)
    )
    
    # 创建一个未来开始的Banner
    future_banner = Banner(
        title="Future Banner",
        description="This banner starts in the future",
        image_url="http://example.com/future_banner.jpg",
        link_type="url",
        link_url="http://example.com/future",
        is_active=True,
        sort_order=101,
        position="home_top",
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=10)
    )
    
    # 创建一个非活跃的Banner
    inactive_banner = Banner(
        title="Inactive Banner",
        description="This banner is inactive",
        image_url="http://example.com/inactive_banner.jpg",
        link_type="url",
        link_url="http://example.com/inactive",
        is_active=False,
        sort_order=102,
        position="home_top",
        start_time=datetime.now() - timedelta(days=1),
        end_time=datetime.now() + timedelta(days=10)
    )
    
    db.add_all([expired_banner, future_banner, inactive_banner])
    db.commit()
    
    # 测试默认获取所有位置的活跃Banner
    active_banners = BannerService.get_active_banners(db)
    
    # 只有原来的test_banners应该是活跃的
    assert len(active_banners) == 3
    
    # 测试获取特定位置的活跃Banner
    position_banners = BannerService.get_active_banners(db, position="home_top")
    assert len(position_banners) == 3
    
    # 测试获取不存在位置的活跃Banner
    no_position_banners = BannerService.get_active_banners(db, position="non_existent")
    assert len(no_position_banners) == 0

def test_record_banner_view(db, create_test_banners):
    """测试记录Banner浏览"""
    banner_id = create_test_banners[0].id
    
    # 获取初始浏览量
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    initial_view_count = banner.view_count
    
    # 记录浏览
    BannerService.record_banner_view(db, banner_id)
    
    # 检查浏览量是否增加
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    assert banner.view_count == initial_view_count + 1
    
    # 再次记录浏览
    BannerService.record_banner_view(db, banner_id)
    
    # 检查浏览量是否再次增加
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    assert banner.view_count == initial_view_count + 2

def test_record_banner_click(db, create_test_banners):
    """测试记录Banner点击"""
    banner_id = create_test_banners[0].id
    
    # 获取初始点击量
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    initial_click_count = banner.click_count
    
    # 记录点击
    click_record = BannerService.record_banner_click(
        db, 
        banner_id, 
        ip_address="192.168.1.1", 
        user_agent="test-agent", 
        device_type="desktop"
    )
    
    # 检查点击记录是否创建
    assert click_record.banner_id == banner_id
    assert click_record.ip_address == "192.168.1.1"
    assert click_record.user_agent == "test-agent"
    assert click_record.device_type == "desktop"
    
    # 检查点击量是否增加
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    assert banner.click_count == initial_click_count + 1
    
    # 检查数据库中是否存在点击记录
    click_in_db = db.query(BannerClick).filter(BannerClick.banner_id == banner_id).first()
    assert click_in_db is not None
    assert click_in_db.ip_address == "192.168.1.1"

def test_get_banner_statistics(db, create_test_banners):
    """测试获取Banner点击统计"""
    banner_id = create_test_banners[0].id
    
    # 创建一些点击记录
    for i in range(5):
        BannerService.record_banner_click(
            db, 
            banner_id, 
            ip_address=f"192.168.1.{i}", 
            user_agent="test-agent", 
            device_type="desktop" if i % 2 == 0 else "mobile"
        )
    
    # 获取统计数据
    stats = BannerService.get_banner_statistics(db)
    
    # 应该有数据
    assert len(stats) > 0
    
    # 检查数据格式
    assert "banner_id" in stats[0]
    assert "banner_title" in stats[0]
    assert "date" in stats[0]
    assert "count" in stats[0]
    
    # 检查特定Banner的数据
    banner_stats = next((s for s in stats if s["banner_id"] == banner_id), None)
    assert banner_stats is not None
    assert banner_stats["count"] == 5
    assert banner_stats["banner_title"] == "Test Banner 1"

def test_get_banner_traffic_by_device(db, create_test_banners):
    """测试获取Banner设备流量分布"""
    banner_id = create_test_banners[0].id
    
    # 创建一些不同设备的点击记录
    for i in range(10):
        device_type = "desktop" if i < 6 else "mobile" if i < 9 else "tablet"
        BannerService.record_banner_click(
            db, 
            banner_id, 
            ip_address=f"192.168.1.{i}", 
            user_agent="test-agent", 
            device_type=device_type
        )
    
    # 获取设备分布数据
    device_stats = BannerService.get_banner_traffic_by_device(db)
    
    # 检查数据
    assert "desktop" in device_stats
    assert "mobile" in device_stats
    assert "tablet" in device_stats
    assert device_stats["desktop"] == 6
    assert device_stats["mobile"] == 3
    assert device_stats["tablet"] == 1 