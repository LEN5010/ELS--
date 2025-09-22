#!/usr/bin/env python3
"""
测试MongoDB日志功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.activity_log import ActivityLog
from app.utils.mongo import MongoDB
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_log_creation():
    """测试日志创建"""
    logger.info("开始测试日志创建...")

    # 测试用户登录日志
    log_id = ActivityLog.log_user_login(1, "测试用户", "127.0.0.1")
    if log_id:
        logger.info(f"用户登录日志创建成功，ID: {log_id}")
    else:
        logger.error("用户登录日志创建失败")

    # 测试测验尝试日志
    log_id = ActivityLog.log_quiz_attempt(1, "测试用户", 1, "词汇测试", 85, 85.5)
    if log_id:
        logger.info(f"测验尝试日志创建成功，ID: {log_id}")
    else:
        logger.error("测验尝试日志创建失败")

    # 测试学习进度日志
    log_id = ActivityLog.log_learning_progress(1, "测试用户", "vocab", 123, "completed")
    if log_id:
        logger.info(f"学习进度日志创建成功，ID: {log_id}")
    else:
        logger.error("学习进度日志创建失败")

def test_log_retrieval():
    """测试日志检索"""
    logger.info("开始测试日志检索...")

    # 获取用户日志
    logs = ActivityLog.get_user_logs(1, limit=5)
    logger.info(f"获取到 {len(logs)} 条用户日志")
    for log in logs:
        logger.info(f"  - {log['action_type']}: {log['timestamp']}")

    # 获取特定操作类型的日志
    logs = ActivityLog.get_logs_by_action_type("user_login", limit=3)
    logger.info(f"获取到 {len(logs)} 条登录日志")

def test_log_statistics():
    """测试日志统计"""
    logger.info("开始测试日志统计...")

    stats = ActivityLog.get_statistics()
    logger.info(f"日志统计信息:")
    logger.info(f"  - 总日志数: {stats.get('total_logs', 0)}")
    logger.info(f"  - 今日日志数: {stats.get('today_logs', 0)}")
    logger.info(f"  - 操作类型统计: {stats.get('action_type_stats', [])}")

def test_mongodb_connection():
    """测试MongoDB连接"""
    logger.info("开始测试MongoDB连接...")

    try:
        client = MongoDB.get_client()
        db = MongoDB.get_database()
        logger.info(f"MongoDB连接成功，数据库: {db.name}")

        # 测试ping
        client.admin.command('ping')
        logger.info("MongoDB连接测试通过")

        return True
    except Exception as e:
        logger.error(f"MongoDB连接测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("="*50)
    logger.info("开始MongoDB日志功能测试")
    logger.info("="*50)

    # 1. 测试MongoDB连接
    if not test_mongodb_connection():
        logger.error("MongoDB连接失败，终止测试")
        return

    # 2. 测试日志创建
    test_log_creation()

    # 3. 测试日志检索
    test_log_retrieval()

    # 4. 测试日志统计
    test_log_statistics()

    logger.info("="*50)
    logger.info("MongoDB日志功能测试完成")
    logger.info("="*50)

if __name__ == '__main__':
    main()