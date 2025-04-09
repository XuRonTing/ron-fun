import pytest
from fastapi import status

# 测试用户管理相关API端点

def test_get_users(client, admin_token, db):
    """测试获取用户列表"""
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert data["total"] >= 2  # 至少有admin_user和normal_user两个用户

def test_get_user_by_id(client, admin_token, db):
    """测试根据ID获取用户详情"""
    # 获取用户列表
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    users = response.json()["items"]
    
    # 找到普通用户
    user_id = None
    for user in users:
        if user["username"] == "user_test":
            user_id = user["id"]
            break
    
    assert user_id is not None
    
    # 获取用户详情
    response = client.get(
        f"/api/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "user_test"
    assert data["email"] == "user@example.com"
    assert "is_active" in data
    assert "points" in data
    assert data["points"] == 1000  # 根据fixture中设置的值

def test_update_user(client, admin_token, db):
    """测试更新用户信息"""
    # 获取用户列表
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    users = response.json()["items"]
    
    # 找到普通用户
    user_id = None
    for user in users:
        if user["username"] == "user_test":
            user_id = user["id"]
            break
    
    assert user_id is not None
    
    # 更新用户信息
    update_data = {
        "nickname": "Updated User Nickname",
        "is_active": False
    }
    response = client.put(
        f"/api/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["nickname"] == update_data["nickname"]
    assert data["is_active"] == update_data["is_active"]
    
    # 确保其他字段未改变
    assert data["username"] == "user_test"
    assert data["email"] == "user@example.com"

def test_adjust_user_points(client, admin_token, db):
    """测试调整用户积分"""
    # 获取用户列表
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    users = response.json()["items"]
    
    # 找到普通用户
    user_id = None
    for user in users:
        if user["username"] == "user_test":
            user_id = user["id"]
            break
    
    assert user_id is not None
    
    # 获取初始积分
    response = client.get(
        f"/api/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    initial_points = response.json()["points"]
    initial_total_points = response.json()["total_points"]
    
    # 增加积分
    points_to_add = 500
    response = client.put(
        f"/api/v1/admin/users/{user_id}/points?points={points_to_add}&reason=测试增加积分",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["points"] == initial_points + points_to_add
    assert data["total_points"] == initial_total_points + points_to_add
    
    # 减少积分
    points_to_reduce = 200
    response = client.put(
        f"/api/v1/admin/users/{user_id}/points?points=-{points_to_reduce}&reason=测试减少积分",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["points"] == initial_points + points_to_add - points_to_reduce
    # 总积分不应该减少
    assert data["total_points"] == initial_total_points + points_to_add

def test_search_users(client, admin_token, db):
    """测试搜索用户功能"""
    # 使用用户名搜索
    response = client.get(
        "/api/v1/admin/users?search=user_test",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert any(user["username"] == "user_test" for user in data["items"])
    
    # 使用邮箱搜索
    response = client.get(
        "/api/v1/admin/users?search=user@example",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert any(user["email"] == "user@example.com" for user in data["items"])
    
    # 使用昵称搜索（可能已更新）
    response = client.get(
        "/api/v1/admin/users?search=User",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1

def test_filter_users_by_status(client, admin_token, db):
    """测试按状态筛选用户"""
    # 筛选活跃用户
    response = client.get(
        "/api/v1/admin/users?status=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert all(user["is_active"] for user in data["items"])
    
    # 筛选非活跃用户
    response = client.get(
        "/api/v1/admin/users?status=false",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert all(not user["is_active"] for user in data["items"]) 