#!/usr/bin/env python3
"""
OPC Platform - 部署状态检查脚本
"""
import requests
import time
import sys
import json
from datetime import datetime

# 配置
BASE_URL = "https://opc-platform.onrender.com"
GITHUB_REPO = "https://github.com/MoKangMedical/opc-platform"
RENDER_DASHBOARD = "https://dashboard.render.com"

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(status, message):
    """打印状态"""
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def check_github():
    """检查GitHub仓库状态"""
    print_header("检查GitHub仓库")
    
    try:
        response = requests.get(GITHUB_REPO, timeout=10)
        if response.status_code == 200:
            print_status(True, f"GitHub仓库可访问: {GITHUB_REPO}")
            return True
        else:
            print_status(False, f"GitHub仓库访问失败: {response.status_code}")
            return False
    except Exception as e:
        print_status(False, f"GitHub仓库检查异常: {e}")
        return False

def check_service_health():
    """检查服务健康状态"""
    print_header("检查服务健康状态")
    
    try:
        url = f"{BASE_URL}/api/health"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_status(True, f"服务健康检查通过")
            print(f"   状态: {data.get('status')}")
            print(f"   平台: {data.get('platform')}")
            print(f"   版本: {data.get('version')}")
            return True
        else:
            print_status(False, f"服务健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_status(False, "服务响应超时（可能正在休眠）")
        print("   提示: Render免费计划在15分钟无请求后会休眠")
        print("   解决: 等待30秒后重试，或访问服务URL唤醒")
        return False
    except Exception as e:
        print_status(False, f"服务健康检查异常: {e}")
        return False

def check_api_endpoints():
    """检查API端点"""
    print_header("检查API端点")
    
    endpoints = [
        ("/api/health", "健康检查"),
        ("/api/projects", "项目列表"),
        ("/api/stats", "统计信息"),
    ]
    
    results = []
    for endpoint, name in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print_status(True, f"{name}: {endpoint}")
                results.append(True)
            else:
                print_status(False, f"{name}: {endpoint} - {response.status_code}")
                results.append(False)
        except Exception as e:
            print_status(False, f"{name}: {endpoint} - {e}")
            results.append(False)
    
    return all(results)

def check_frontend():
    """检查前端页面"""
    print_header("检查前端页面")
    
    pages = [
        ("/", "首页"),
        ("/docs/index.html", "首页HTML"),
        ("/docs/login.html", "登录页"),
        ("/docs/register.html", "注册页"),
    ]
    
    results = []
    for path, name in pages:
        try:
            url = f"{BASE_URL}{path}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print_status(True, f"{name}: {path}")
                results.append(True)
            else:
                print_status(False, f"{name}: {path} - {response.status_code}")
                results.append(False)
        except Exception as e:
            print_status(False, f"{name}: {path} - {e}")
            results.append(False)
    
    return all(results)

def check_database():
    """检查数据库连接"""
    print_header("检查数据库连接")
    
    try:
        url = f"{BASE_URL}/api/stats"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_status(True, "数据库连接正常")
            print(f"   项目数: {data.get('projects', 0)}")
            print(f"   课程数: {data.get('courses', 0)}")
            print(f"   用户数: {data.get('users', 0)}")
            return True
        else:
            print_status(False, f"数据库检查失败: {response.status_code}")
            return False
    except Exception as e:
        print_status(False, f"数据库检查异常: {e}")
        return False

def wake_up_service():
    """唤醒服务"""
    print_header("唤醒服务")
    
    print("   发送请求唤醒服务（Render免费计划会休眠）...")
    
    try:
        url = f"{BASE_URL}/api/health"
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            print_status(True, "服务已唤醒")
            return True
        else:
            print_status(False, f"唤醒失败: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_status(False, "唤醒超时")
        print("   提示: 服务可能正在启动中，请等待1-2分钟后重试")
        return False
    except Exception as e:
        print_status(False, f"唤醒异常: {e}")
        return False

def print_deployment_info():
    """打印部署信息"""
    print_header("部署信息")
    
    print(f"📡 服务地址: {BASE_URL}")
    print(f"📦 GitHub仓库: {GITHUB_REPO}")
    print(f"🎛️ Render控制台: {RENDER_DASHBOARD}")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📋 常用命令:")
    print("   测试API: curl https://opc-platform.onrender.com/api/health")
    print("   查看日志: 登录Render Dashboard → Logs")
    print("   手动部署: Render Dashboard → Manual Deploy")

def main():
    """主函数"""
    print_header("OPC Platform - 部署状态检查")
    
    # 检查计数
    total_checks = 0
    passed_checks = 0
    
    # 1. 检查GitHub
    total_checks += 1
    if check_github():
        passed_checks += 1
    
    # 2. 唤醒服务
    total_checks += 1
    if wake_up_service():
        passed_checks += 1
    
    # 等待服务完全启动
    print("\n⏳ 等待服务完全启动...")
    time.sleep(3)
    
    # 3. 检查服务健康
    total_checks += 1
    if check_service_health():
        passed_checks += 1
    
    # 4. 检查API端点
    total_checks += 1
    if check_api_endpoints():
        passed_checks += 1
    
    # 5. 检查前端
    total_checks += 1
    if check_frontend():
        passed_checks += 1
    
    # 6. 检查数据库
    total_checks += 1
    if check_database():
        passed_checks += 1
    
    # 打印部署信息
    print_deployment_info()
    
    # 打印结果
    print_header("检查结果")
    print(f"✅ 通过: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print("\n🎉 所有检查通过！服务部署成功！")
        print(f"\n👉 访问服务: {BASE_URL}")
        return 0
    elif passed_checks >= total_checks - 1:
        print("\n⚠️ 大部分检查通过，服务基本可用")
        print("\n可能的问题:")
        print("  - 服务刚启动，部分功能需要预热")
        print("  - 免费计划限制导致响应较慢")
        return 0
    else:
        print("\n❌ 多个检查失败，请检查部署状态")
        print("\n故障排除:")
        print("  1. 登录Render Dashboard查看部署日志")
        print("  2. 检查GitHub仓库是否有最新代码")
        print("  3. 确认数据库服务已创建")
        return 1

if __name__ == "__main__":
    sys.exit(main())
