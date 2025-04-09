import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.api.deps import get_db
from app.core.config import settings
from app.models.user import User
from app.models.banner import Banner
from app.models.application import Application
from app.models.product import Product, ProductCategory
from app.core.security import get_password_hash, create_access_token

# 使用SQLite内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库和表
def setup_database():
    from app.db.base_class import Base
    Base.metadata.create_all(bind=engine)

# 测试前清理数据库
def teardown_database():
    from app.db.base_class import Base
    Base.metadata.drop_all(bind=engine)

# 覆盖依赖，使用测试数据库
@pytest.fixture
def db():
    # 设置测试数据库
    setup_database()
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        # 清理数据库
        teardown_database()

# 创建测试客户端
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

    # 测试后恢复原始依赖
    app.dependency_overrides.clear()

# 创建超级管理员用户
@pytest.fixture
def admin_token(db):
    # 创建超级管理员
    admin_user = User(
        username="admin_test",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        nickname="Test Admin",
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": admin_user.username}
    )
    return access_token

# 创建普通用户
@pytest.fixture
def normal_token(db):
    # 创建普通用户
    normal_user = User(
        username="user_test",
        email="user@example.com",
        hashed_password=get_password_hash("user123"),
        is_active=True,
        is_superuser=False,
        nickname="Test User",
        points=1000,
        total_points=1000,
    )
    db.add(normal_user)
    db.commit()
    db.refresh(normal_user)
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": normal_user.username}
    )
    return access_token

# 创建测试Banner
@pytest.fixture
def create_test_banners(db):
    # 创建Banner数据
    banners = [
        Banner(
            title=f"Test Banner {i}",
            description=f"Test Banner Description {i}",
            image_url=f"http://example.com/banner{i}.jpg",
            link_type="url",
            link_url="http://example.com",
            is_active=True,
            sort_order=i,
            position="home_top",
        )
        for i in range(1, 4)
    ]
    db.add_all(banners)
    db.commit()
    
    # 刷新所有Banner以获取ID
    for banner in banners:
        db.refresh(banner)
    
    return banners

# 创建测试应用
@pytest.fixture
def create_test_applications(db):
    # 创建Application数据
    applications = [
        Application(
            name=f"Test App {i}",
            description=f"Test App Description {i}",
            icon=f"http://example.com/app{i}.jpg",
            link_type="url",
            link_url="http://example.com",
            is_active=True,
            sort_order=i,
            position="home_app",
        )
        for i in range(1, 4)
    ]
    db.add_all(applications)
    db.commit()
    
    # 刷新所有应用以获取ID
    for app in applications:
        db.refresh(app)
    
    return applications

# 创建测试商品分类
@pytest.fixture
def create_test_product_categories(db):
    # 创建ProductCategory数据
    categories = [
        ProductCategory(
            name=f"Category {i}",
            description=f"Category Description {i}",
            icon=f"http://example.com/category{i}.jpg",
        )
        for i in range(1, 4)
    ]
    db.add_all(categories)
    db.commit()
    
    # 刷新所有分类以获取ID
    for category in categories:
        db.refresh(category)
    
    return categories

# 创建测试商品
@pytest.fixture
def create_test_products(db, create_test_product_categories):
    # 使用之前创建的分类
    categories = create_test_product_categories
    
    # 创建Product数据
    products = []
    for i in range(1, 10):
        product = Product(
            name=f"Product {i}",
            description=f"Product Description {i}",
            category_id=categories[i % 3].id,
            image_url=f"http://example.com/product{i}.jpg",
            points_price=i * 100,
            stock=100,
            is_active=True,
            sort_order=i,
        )
        products.append(product)
    
    db.add_all(products)
    db.commit()
    
    # 刷新所有商品以获取ID
    for product in products:
        db.refresh(product)
    
    return products 