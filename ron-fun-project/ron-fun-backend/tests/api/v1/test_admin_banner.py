import pytest
from fastapi import status

# 测试Banner相关API端点

@pytest.mark.parametrize(
    "skip,limit,expected_count",
    [
        (0, 10, 3),  # 默认分页，应返回所有3个Banner
        (1, 1, 1),   # 跳过1个，限制1个，应返回1个Banner
        (0, 2, 2),   # 不跳过，限制2个，应返回2个Banner
        (3, 10, 0),  # 跳过全部，应返回0个Banner
    ]
)
def test_get_banners(client, admin_token, create_test_banners, skip, limit, expected_count):
    """测试获取Banner列表，验证分页功能"""
    response = client.get(
        f"/api/v1/admin/banners?skip={skip}&limit={limit}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == expected_count
    assert data["total"] == 3  # 总数应为3个Banner
    if expected_count > 0:
        assert "id" in data["items"][0]
        assert "title" in data["items"][0]
        assert "image_url" in data["items"][0]

def test_get_banner_by_id(client, admin_token, create_test_banners):
    """测试根据ID获取Banner详情"""
    banner_id = create_test_banners[0].id
    response = client.get(
        f"/api/v1/admin/banners/{banner_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == banner_id
    assert data["title"] == "Test Banner 1"
    assert data["image_url"] == "http://example.com/banner1.jpg"

def test_create_banner(client, admin_token):
    """测试创建Banner"""
    new_banner = {
        "title": "New Test Banner",
        "description": "New Banner Description",
        "image_url": "http://example.com/new_banner.jpg",
        "link_type": "url",
        "link_url": "http://example.com/new",
        "is_active": True,
        "sort_order": 10,
        "position": "home_bottom"
    }
    response = client.post(
        "/api/v1/admin/banners",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_banner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == new_banner["title"]
    assert data["description"] == new_banner["description"]
    assert data["position"] == new_banner["position"]
    assert "id" in data

def test_update_banner(client, admin_token, create_test_banners):
    """测试更新Banner"""
    banner_id = create_test_banners[0].id
    update_data = {
        "title": "Updated Banner Title",
        "is_active": False
    }
    response = client.put(
        f"/api/v1/admin/banners/{banner_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == banner_id
    assert data["title"] == update_data["title"]
    assert data["is_active"] == update_data["is_active"]
    # 确保其他字段未改变
    assert data["image_url"] == "http://example.com/banner1.jpg"

def test_access_denied_for_normal_user(client, normal_token, create_test_banners):
    """测试普通用户无权访问管理API"""
    response = client.get(
        "/api/v1/admin/banners",
        headers={"Authorization": f"Bearer {normal_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_banner_statistics(client, admin_token, create_test_banners, db):
    """测试Banner点击统计功能"""
    # 先创建一些点击记录
    banner_id = create_test_banners[0].id
    
    # 模拟API点击，因为这是直接访问service，所以无法通过路由中间件进行验证
    from app.services.banner_service import BannerService
    for i in range(5):
        BannerService.record_banner_click(
            db, 
            banner_id, 
            ip_address="127.0.0.1", 
            user_agent="test-agent", 
            device_type="desktop"
        )
    
    # 测试获取点击记录
    response = client.get(
        f"/api/v1/admin/banners/{banner_id}/clicks",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 5
    assert data["total"] == 5
    
    # 测试获取统计数据
    response = client.get(
        "/api/v1/admin/banners/statistics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert len(stats) > 0
    assert "banner_id" in stats[0]
    assert "count" in stats[0]
    assert "date" in stats[0]