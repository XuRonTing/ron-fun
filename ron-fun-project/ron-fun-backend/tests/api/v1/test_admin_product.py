import pytest
from fastapi import status

# 测试商品相关API端点

@pytest.mark.parametrize(
    "skip,limit,expected_count",
    [
        (0, 10, 9),   # 默认分页，应返回所有9个商品
        (1, 2, 2),    # 跳过1个，限制2个，应返回2个商品
        (0, 5, 5),    # 不跳过，限制5个，应返回5个商品
        (10, 10, 0),  # 跳过全部，应返回0个商品
    ]
)
def test_get_products(client, admin_token, create_test_products, skip, limit, expected_count):
    """测试获取商品列表，验证分页功能"""
    response = client.get(
        f"/api/v1/admin/products?skip={skip}&limit={limit}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == expected_count
    assert data["total"] == 9  # 总数应为9个商品
    if expected_count > 0:
        assert "id" in data["items"][0]
        assert "name" in data["items"][0]
        assert "points_price" in data["items"][0]

def test_get_product_by_id(client, admin_token, create_test_products):
    """测试根据ID获取商品详情"""
    product_id = create_test_products[0].id
    response = client.get(
        f"/api/v1/admin/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Product 1"
    assert data["points_price"] == 100

def test_create_product(client, admin_token, create_test_product_categories):
    """测试创建商品"""
    category_id = create_test_product_categories[0].id
    new_product = {
        "name": "New Test Product",
        "description": "New Product Description",
        "category_id": category_id,
        "image_url": "http://example.com/new_product.jpg",
        "points_price": 888,
        "stock": 50,
        "is_active": True,
        "sort_order": 100
    }
    response = client.post(
        "/api/v1/admin/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_product
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == new_product["name"]
    assert data["description"] == new_product["description"]
    assert data["points_price"] == new_product["points_price"]
    assert "id" in data

def test_update_product(client, admin_token, create_test_products):
    """测试更新商品"""
    product_id = create_test_products[0].id
    update_data = {
        "name": "Updated Product Name",
        "points_price": 150,
        "is_active": False
    }
    response = client.put(
        f"/api/v1/admin/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == update_data["name"]
    assert data["points_price"] == update_data["points_price"]
    assert data["is_active"] == update_data["is_active"]
    # 确保其他字段未改变
    assert data["description"] == "Product Description 1"

def test_filter_products_by_category(client, admin_token, create_test_products, create_test_product_categories):
    """测试按分类筛选商品"""
    category_id = create_test_product_categories[0].id
    response = client.get(
        f"/api/v1/admin/products?category_id={category_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert all(product["category_id"] == category_id for product in data["items"])

def test_search_products(client, admin_token, create_test_products):
    """测试搜索商品功能"""
    # 搜索"Product 1"
    response = client.get(
        "/api/v1/admin/products?search=Product 1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert any("Product 1" in product["name"] for product in data["items"])

def test_filter_products_by_status(client, admin_token, create_test_products):
    """测试按状态筛选商品"""
    # 先更新一个商品为非活跃状态
    product_id = create_test_products[0].id
    update_data = {"is_active": False}
    client.put(
        f"/api/v1/admin/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    
    # 筛选活跃商品
    response = client.get(
        "/api/v1/admin/products?status=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert all(product["is_active"] for product in data["items"])
    
    # 筛选非活跃商品
    response = client.get(
        "/api/v1/admin/products?status=false",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert all(not product["is_active"] for product in data["items"])

def test_get_orders(client, admin_token):
    """测试获取订单列表"""
    # 注意：此测试仅验证API是否可调用，因为我们没有创建订单数据
    response = client.get(
        "/api/v1/admin/orders",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data 