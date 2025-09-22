#!/usr/bin/env python3
"""
测试日志API接口
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5001/api"

def test_basic_endpoints():
    """测试基础端点"""
    logger.info("测试基础端点...")

    # 测试根端点
    response = requests.get("http://localhost:5001/")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"根端点测试通过: {data['message']}")
        logger.info(f"可用端点: {list(data['endpoints'].keys())}")
    else:
        logger.error(f"根端点测试失败: {response.status_code}")

    # 测试健康检查
    response = requests.get("http://localhost:5001/health")
    if response.status_code == 200:
        logger.info(f"健康检查通过: {response.json()}")
    else:
        logger.error(f"健康检查失败: {response.status_code}")

def test_user_auth():
    """测试用户认证，返回token"""
    logger.info("测试用户认证...")

    # 测试用户登录（假设有测试用户）
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        logger.info("用户登录成功")
        return data['data']['token']
    else:
        logger.warning(f"用户登录失败: {response.status_code}, 可能需要先注册用户")

        # 尝试注册用户
        register_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "nickname": "测试用户"
        }

        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            data = response.json()
            logger.info("用户注册成功")
            return data['data']['token']
        else:
            logger.error(f"用户注册失败: {response.status_code} - {response.text}")
            return None

def test_log_apis(token):
    """测试日志API"""
    if not token:
        logger.error("没有有效的认证token，跳过日志API测试")
        return

    headers = {"Authorization": f"Bearer {token}"}
    logger.info("测试日志API...")

    # 1. 测试创建日志
    log_data = {
        "action_type": "api_test",
        "details": {
            "test_type": "automated_test",
            "timestamp": "2025-09-22T04:55:00Z"
        }
    }

    response = requests.post(f"{BASE_URL}/logs/create", json=log_data, headers=headers)
    if response.status_code == 200:
        logger.info("创建日志测试通过")
    else:
        logger.error(f"创建日志测试失败: {response.status_code} - {response.text}")

    # 2. 测试获取我的日志
    response = requests.get(f"{BASE_URL}/logs/my-logs?page=1&per_page=5", headers=headers)
    if response.status_code == 200:
        data = response.json()
        logs = data['data']['logs']
        logger.info(f"获取我的日志测试通过，找到 {len(logs)} 条日志")
        for log in logs[:3]:  # 显示前3条
            logger.info(f"  - {log['action_type']}: {log['timestamp']}")
    else:
        logger.error(f"获取我的日志测试失败: {response.status_code} - {response.text}")

    # 3. 测试记录学习进度
    progress_data = {
        "content_type": "vocab",
        "content_id": 123,
        "action": "completed"
    }

    response = requests.post(f"{BASE_URL}/logs/log-learning-progress", json=progress_data, headers=headers)
    if response.status_code == 200:
        logger.info("记录学习进度测试通过")
    else:
        logger.error(f"记录学习进度测试失败: {response.status_code} - {response.text}")

    # 4. 测试记录测验尝试
    quiz_data = {
        "quiz_id": 1,
        "quiz_title": "API测试测验",
        "score": 90,
        "accuracy": 90.0
    }

    response = requests.post(f"{BASE_URL}/logs/log-quiz-attempt", json=quiz_data, headers=headers)
    if response.status_code == 200:
        logger.info("记录测验尝试测试通过")
    else:
        logger.error(f"记录测验尝试测试失败: {response.status_code} - {response.text}")

    # 5. 测试获取最近活动
    response = requests.get(f"{BASE_URL}/logs/recent-activities?limit=5", headers=headers)
    if response.status_code == 200:
        data = response.json()
        activities = data['data']['recent_activities']
        logger.info(f"获取最近活动测试通过，找到 {len(activities)} 条活动")
    else:
        logger.error(f"获取最近活动测试失败: {response.status_code} - {response.text}")

def test_admin_apis(token):
    """测试管理员API（可能会失败，因为普通用户没有管理员权限）"""
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    logger.info("测试管理员日志API（可能需要管理员权限）...")

    # 测试获取日志统计
    response = requests.get(f"{BASE_URL}/logs/statistics", headers=headers)
    if response.status_code == 200:
        data = response.json()
        logger.info(f"获取日志统计测试通过: {data['data']}")
    elif response.status_code == 403:
        logger.info("获取日志统计需要管理员权限，跳过")
    else:
        logger.error(f"获取日志统计测试失败: {response.status_code} - {response.text}")

def main():
    """主测试函数"""
    logger.info("="*50)
    logger.info("开始日志API接口测试")
    logger.info("="*50)

    # 1. 测试基础端点
    test_basic_endpoints()

    # 2. 测试用户认证
    token = test_user_auth()

    # 3. 测试日志API
    test_log_apis(token)

    # 4. 测试管理员API
    test_admin_apis(token)

    logger.info("="*50)
    logger.info("日志API接口测试完成")
    logger.info("="*50)

if __name__ == '__main__':
    main()