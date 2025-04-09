import pytest
import time
from sqlalchemy import func, text

from app.models.user import User
from app.models.banner import Banner, BannerClick
from app.models.application import Application, ApplicationClick
from app.models.product import Product, ProductCategory

# 注意：性能测试会在本地运行，但主要用于CI/CD环境中监控性能变化

@pytest.mark.performance
def test_banner_query_performance(db, create_test_banners):
    """测试Banner查询性能"""
    # 创建更多测试数据
    banners = []
    for i in range(100):
        banner = Banner(
            title=f"Performance Test Banner {i}",
            description=f"Performance Test Description {i}",
            image_url=f"http://example.com/perf_banner{i}.jpg",
            link_type="url",
            link_url="http://example.com",
            is_active=True,
            sort_order=i,
            position="performance_test",
        )
        banners.append(banner)
    
    db.add_all(banners)
    db.commit()
    
    # 测试基本查询性能
    start_time = time.time()
    result = db.query(Banner).all()
    query_time = time.time() - start_time
    
    print(f"Banner基本查询时间: {query_time:.6f}秒，结果数量: {len(result)}")
    assert query_time < 1.0, "Banner基本查询耗时过长"
    
    # 测试带条件的查询性能
    start_time = time.time()
    result = db.query(Banner).filter(Banner.position == "performance_test").all()
    query_time = time.time() - start_time
    
    print(f"Banner条件查询时间: {query_time:.6f}秒，结果数量: {len(result)}")
    assert query_time < 1.0, "Banner条件查询耗时过长"

@pytest.mark.performance
def test_user_search_performance(db):
    """测试用户搜索性能"""
    # 创建更多测试数据
    users = []
    for i in range(100):
        user = User(
            username=f"perf_user_{i}",
            email=f"perf_user_{i}@example.com",
            hashed_password="hashed_password",
            is_active=True,
            nickname=f"Performance User {i}",
            points=i * 100,
            total_points=i * 100,
        )
        users.append(user)
    
    db.add_all(users)
    db.commit()
    
    # 测试模糊搜索性能
    start_time = time.time()
    result = db.query(User).filter(User.username.like("%perf_user%")).all()
    query_time = time.time() - start_time
    
    print(f"用户模糊搜索时间: {query_time:.6f}秒，结果数量: {len(result)}")
    assert query_time < 1.0, "用户模糊搜索耗时过长"
    
    # 测试复杂条件查询性能
    start_time = time.time()
    result = db.query(User).filter(
        User.username.like("%perf_user%"),
        User.points > 5000,
        User.is_active == True
    ).all()
    query_time = time.time() - start_time
    
    print(f"用户复杂条件查询时间: {query_time:.6f}秒，结果数量: {len(result)}")
    assert query_time < 1.0, "用户复杂条件查询耗时过长"

@pytest.mark.performance
def test_join_query_performance(db, create_test_banners):
    """测试关联查询性能"""
    # 添加Banner点击数据
    banner_id = create_test_banners[0].id
    clicks = []
    for i in range(200):
        click = BannerClick(
            banner_id=banner_id,
            ip_address="127.0.0.1",
            user_agent="test-agent",
            device_type="desktop" if i % 2 == 0 else "mobile"
        )
        clicks.append(click)
    
    db.add_all(clicks)
    db.commit()
    
    # 测试关联查询性能
    start_time = time.time()
    result = db.query(
        Banner.title,
        func.count(BannerClick.id).label("click_count")
    ).join(
        BannerClick, Banner.id == BannerClick.banner_id
    ).group_by(
        Banner.id
    ).all()
    query_time = time.time() - start_time
    
    print(f"Banner关联查询时间: {query_time:.6f}秒，结果数量: {len(result)}")
    assert query_time < 1.0, "Banner关联查询耗时过长"
    
    # 测试复杂聚合查询性能
    start_time = time.time()
    result = db.query(
        Banner.title,
        Banner.position,
        func.count(BannerClick.id).label("click_count"),
        func.count(func.distinct(BannerClick.ip_address)).label("unique_ips")
    ).join(
        BannerClick, Banner.id == BannerClick.banner_id
    ).filter(
        Banner.is_active == True
    ).group_by(
        Banner.id, Banner.position
    ).order_by(
        func.count(BannerClick.id).desc()
    ).all()
    query_time = time.time() - start_time
    
    print(f"Banner复杂聚合查询时间: {query_time:.6f}秒，结果数量: {len(result)}")
    assert query_time < 1.0, "Banner复杂聚合查询耗时过长"

@pytest.mark.performance
def test_transaction_performance(db):
    """测试事务性能"""
    # 测试批量插入性能
    products = []
    for i in range(100):
        product = Product(
            name=f"Batch Product {i}",
            description=f"Batch Product Description {i}",
            category_id=1,  # 假设ID为1的分类存在
            image_url=f"http://example.com/batch_product{i}.jpg",
            points_price=i * 10,
            stock=100,
            is_active=True,
            sort_order=i,
        )
        products.append(product)
    
    start_time = time.time()
    db.add_all(products)
    db.commit()
    transaction_time = time.time() - start_time
    
    print(f"批量插入100个商品时间: {transaction_time:.6f}秒")
    assert transaction_time < 2.0, "批量插入耗时过长"
    
    # 测试批量更新性能
    start_time = time.time()
    db.execute(
        text("UPDATE product SET stock = stock + 10 WHERE is_active = 1")
    )
    db.commit()
    update_time = time.time() - start_time
    
    print(f"批量更新商品库存时间: {update_time:.6f}秒")
    assert update_time < 1.0, "批量更新耗时过长" 