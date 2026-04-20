#!/usr/bin/env python3
"""
OPC Platform - API测试脚本
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_register():
    """测试用户注册"""
    print("\n🔍 测试用户注册...")
    try:
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpassword123",
            "display_name": "测试用户"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 注册成功: 用户ID {data['user']['id']}")
            return data['access_token'], data['user']
        else:
            print(f"❌ 注册失败: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        return None, None

def test_login(username, password):
    """测试用户登录"""
    print("\n🔍 测试用户登录...")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功: 用户 {data['user']['username']}")
            return data['access_token']
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_get_user_info(token):
    """测试获取用户信息"""
    print("\n🔍 测试获取用户信息...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取用户信息成功: {data['username']}")
            return data
        else:
            print(f"❌ 获取用户信息失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return None

def test_update_user(token):
    """测试更新用户信息"""
    print("\n🔍 测试更新用户信息...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        update_data = {
            "display_name": "更新后的测试用户",
            "bio": "这是一个测试简介",
            "location": "北京",
            "website": "https://example.com"
        }
        
        response = requests.put(f"{BASE_URL}/api/auth/me", headers=headers, json=update_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 更新用户信息成功: {data['display_name']}")
            return True
        else:
            print(f"❌ 更新用户信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 更新用户信息异常: {e}")
        return False

def test_list_projects():
    """测试获取项目列表"""
    print("\n🔍 测试获取项目列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/projects")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取项目列表成功: 共 {data['total']} 个项目")
            return data['projects']
        else:
            print(f"❌ 获取项目列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取项目列表异常: {e}")
        return []

def test_matching(token):
    """测试匹配功能"""
    print("\n🔍 测试匹配功能...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取推荐项目
        response = requests.get(f"{BASE_URL}/api/matching/users/me/recommended-projects", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取推荐项目成功: 共 {data['total']} 个推荐")
            return True
        else:
            print(f"❌ 获取推荐项目失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试匹配功能异常: {e}")
        return False

def test_create_order(token):
    """测试创建订单"""
    print("\n🔍 测试创建订单...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        order_data = {
            "title": "测试订单",
            "amount": 100.00,
            "description": "这是一个测试订单",
            "currency": "CNY"
        }
        
        response = requests.post(f"{BASE_URL}/api/payment/orders", headers=headers, json=order_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 创建订单成功: 订单号 {data['order_no']}")
            return data['order_no']
        else:
            print(f"❌ 创建订单失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 创建订单异常: {e}")
        return None

def test_get_order(token, order_no):
    """测试获取订单详情"""
    print("\n🔍 测试获取订单详情...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/payment/orders/{order_no}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取订单详情成功: {data['title']}")
            return True
        else:
            print(f"❌ 获取订单详情失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取订单详情异常: {e}")
        return False

def test_stats():
    """测试获取统计信息"""
    print("\n🔍 测试获取统计信息...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取统计信息成功:")
            print(f"   - 项目数: {data.get('projects', 0)}")
            print(f"   - 课程数: {data.get('courses', 0)}")
            print(f"   - 用户数: {data.get('users', 0)}")
            return True
        else:
            print(f"❌ 获取统计信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取统计信息异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("OPC Platform - API测试")
    print("=" * 60)
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 1. 健康检查
    total_tests += 1
    if test_health():
        passed_tests += 1
    
    # 2. 用户注册
    total_tests += 1
    token, user = test_register()
    if token:
        passed_tests += 1
    
    if not token:
        print("\n❌ 无法获取token，跳过后续测试")
        return
    
    # 3. 用户登录（使用注册的用户）
    total_tests += 1
    login_token = test_login(user['username'], 'testpassword123')
    if login_token:
        passed_tests += 1
    
    # 4. 获取用户信息
    total_tests += 1
    if test_get_user_info(token):
        passed_tests += 1
    
    # 5. 更新用户信息
    total_tests += 1
    if test_update_user(token):
        passed_tests += 1
    
    # 6. 获取项目列表
    total_tests += 1
    projects = test_list_projects()
    if projects:
        passed_tests += 1
    
    # 7. 测试匹配功能
    total_tests += 1
    if test_matching(token):
        passed_tests += 1
    
    # 8. 创建订单
    total_tests += 1
    order_no = test_create_order(token)
    if order_no:
        passed_tests += 1
    
    # 9. 获取订单详情
    if order_no:
        total_tests += 1
        if test_get_order(token, order_no):
            passed_tests += 1
    
    # 10. 获取统计信息
    total_tests += 1
    if test_stats():
        passed_tests += 1
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print(f"测试完成: {passed_tests}/{total_tests} 通过")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
