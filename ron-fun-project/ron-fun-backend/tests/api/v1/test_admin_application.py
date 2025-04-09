import pytest
from fastapi import status

# 测试应用相关API端点

@pytest.mark.parametrize(
    "skip,limit,expected_count",
    [
        (0, 10, 3),  # 默认分页，应返回所有3个应用
        (1, 1, 1),   # 跳过1个，限制1个，应返回1个应用
        (0, 2, 2),   # 不跳过，限制2个，应返回2个应用
        (3, 10, 0),  # 跳过全部，应返回0个应用
    ]
)
def test_get_applications(client, admin_token, create_test_applications, skip, limit, expected_count):
    """测试获取应用列表，验证分页功能"""
    response = client.get(
        f"/api/v1/admin/applications?skip={skip}&limit={limit}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == expected_count
    assert data["total"] == 3  # 总数应为3个应用
    if expected_count > 0:
        assert "id" in data["items"][0]
        assert "name" in data["items"][0]
        assert "icon" in data["items"][0]

def test_get_application_by_id(client, admin_token, create_test_applications):
    """测试根据ID获取应用详情"""
    app_id = create_test_applications[0].id
    response = client.get(
        f"/api/v1/admin/applications/{app_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == app_id
    assert data["name"] == "Test App 1"
    assert data["icon"] == "http://example.com/app1.jpg"

def test_create_application(client, admin_token):
    """测试创建应用"""
    new_app = {
        "name": "New Test App",
        "description": "New App Description",
        "icon": "http://example.com/new_app.jpg",
        "link_type": "url",
        "link_url": "http://example.com/new",
        "is_active": True,
        "sort_order": 10,
        "position": "home_feature"
    }
    response = client.post(
        "/api/v1/admin/applications",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_app
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == new_app["name"]
    assert data["description"] == new_app["description"]
    assert data["position"] == new_app["position"]
    assert "id" in data

def test_update_application(client, admin_token, create_test_applications):
    """测试更新应用"""
    app_id = create_test_applications[0].id
    update_data = {
        "name": "Updated App Name",
        "is_active": False
    }
    response = client.put(
        f"/api/v1/admin/applications/{app_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == app_id
    assert data["name"] == update_data["name"]
    assert data["is_active"] == update_data["is_active"]
    # 确保其他字段未改变
    assert data["icon"] == "http://example.com/app1.jpg"

def test_application_statistics(client, admin_token, create_test_applications, db):
    """测试应用点击统计功能"""
    # 先创建一些点击记录
    app_id = create_test_applications[0].id
    
    # 模拟API点击，因为这是直接访问service，所以无法通过路由中间件进行验证
    from app.services.application_service import ApplicationService
    for i in range(5):
        ApplicationService.record_application_click(
            db, 
            app_id, 
            ip_address="127.0.0.1", 
            user_agent="test-agent", 
            device_type="desktop"
        )
    
    # 测试获取点击记录
    response = client.get(
        f"/api/v1/admin/applications/{app_id}/clicks",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 5
    assert data["total"] == 5
    
    # 测试获取统计数据
    response = client.get(
        "/api/v1/admin/applications/statistics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert len(stats) > 0
    assert "application_id" in stats[0]
    assert "count" in stats[0]
    assert "date" in stats[0] 