from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from app.utils.mongo import get_mongo_collection
import logging

logger = logging.getLogger(__name__)

class ActivityLog:
    """用户活动日志模型"""

    COLLECTION_NAME = 'activity_logs'

    @classmethod
    def create_log(cls, user_id: int, nickname: str, action_type: str, details: Dict[str, Any]) -> Optional[str]:
        """
        创建活动日志
        :param user_id: 用户ID
        :param nickname: 用户昵称
        :param action_type: 操作类型
        :param details: 详细信息
        :return: 日志ID
        """
        try:
            log_data = {
                'user_id': user_id,
                'nickname': nickname,
                'action_type': action_type,
                'timestamp': datetime.now(timezone.utc),
                'details': details
            }

            with get_mongo_collection(cls.COLLECTION_NAME) as collection:
                result = collection.insert_one(log_data)
                return str(result.inserted_id)

        except Exception as e:
            logger.error(f"创建活动日志失败: {e}")
            return None

    @classmethod
    def get_user_logs(cls, user_id: int, limit: int = 50, skip: int = 0) -> List[Dict]:
        """
        获取用户活动日志
        :param user_id: 用户ID
        :param limit: 限制条数
        :param skip: 跳过条数
        :return: 日志列表
        """
        try:
            with get_mongo_collection(cls.COLLECTION_NAME) as collection:
                cursor = collection.find(
                    {'user_id': user_id}
                ).sort('timestamp', -1).skip(skip).limit(limit)

                logs = []
                for log in cursor:
                    log['_id'] = str(log['_id'])
                    logs.append(log)
                return logs

        except Exception as e:
            logger.error(f"获取用户活动日志失败: {e}")
            return []

    @classmethod
    def get_logs_by_action_type(cls, action_type: str, limit: int = 50, skip: int = 0) -> List[Dict]:
        """
        根据操作类型获取日志
        :param action_type: 操作类型
        :param limit: 限制条数
        :param skip: 跳过条数
        :return: 日志列表
        """
        try:
            with get_mongo_collection(cls.COLLECTION_NAME) as collection:
                cursor = collection.find(
                    {'action_type': action_type}
                ).sort('timestamp', -1).skip(skip).limit(limit)

                logs = []
                for log in cursor:
                    log['_id'] = str(log['_id'])
                    logs.append(log)
                return logs

        except Exception as e:
            logger.error(f"根据操作类型获取日志失败: {e}")
            return []

    @classmethod
    def get_logs_by_date_range(cls, start_date: datetime, end_date: datetime,
                              user_id: Optional[int] = None, limit: int = 100, skip: int = 0) -> List[Dict]:
        """
        根据日期范围获取日志
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param user_id: 可选用户ID
        :param limit: 限制条数
        :param skip: 跳过条数
        :return: 日志列表
        """
        try:
            query = {
                'timestamp': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }

            if user_id:
                query['user_id'] = user_id

            with get_mongo_collection(cls.COLLECTION_NAME) as collection:
                cursor = collection.find(query).sort('timestamp', -1).skip(skip).limit(limit)

                logs = []
                for log in cursor:
                    log['_id'] = str(log['_id'])
                    logs.append(log)
                return logs

        except Exception as e:
            logger.error(f"根据日期范围获取日志失败: {e}")
            return []

    @classmethod
    def get_statistics(cls, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取日志统计信息
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 统计信息
        """
        try:
            pipeline = []

            # 日期过滤
            if start_date or end_date:
                match_stage = {}
                if start_date and end_date:
                    match_stage['timestamp'] = {'$gte': start_date, '$lte': end_date}
                elif start_date:
                    match_stage['timestamp'] = {'$gte': start_date}
                elif end_date:
                    match_stage['timestamp'] = {'$lte': end_date}
                pipeline.append({'$match': match_stage})

            # 统计各种操作类型的数量
            pipeline.extend([
                {
                    '$group': {
                        '_id': '$action_type',
                        'count': {'$sum': 1},
                        'unique_users': {'$addToSet': '$user_id'}
                    }
                },
                {
                    '$project': {
                        'action_type': '$_id',
                        'count': 1,
                        'unique_user_count': {'$size': '$unique_users'},
                        '_id': 0
                    }
                }
            ])

            with get_mongo_collection(cls.COLLECTION_NAME) as collection:
                result = list(collection.aggregate(pipeline))

                # 总日志数
                total_logs = collection.count_documents({})

                # 今日日志数
                today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                today_logs = collection.count_documents({
                    'timestamp': {'$gte': today_start}
                })

                return {
                    'total_logs': total_logs,
                    'today_logs': today_logs,
                    'action_type_stats': result
                }

        except Exception as e:
            logger.error(f"获取日志统计失败: {e}")
            return {}

    @classmethod
    def log_user_login(cls, user_id: int, nickname: str, ip_address: str = None) -> Optional[str]:
        """记录用户登录"""
        details = {'ip_address': ip_address} if ip_address else {}
        return cls.create_log(user_id, nickname, 'user_login', details)

    @classmethod
    def log_user_logout(cls, user_id: int, nickname: str) -> Optional[str]:
        """记录用户登出"""
        return cls.create_log(user_id, nickname, 'user_logout', {})

    @classmethod
    def log_quiz_attempt(cls, user_id: int, nickname: str, quiz_id: int,
                        quiz_title: str, score: int, accuracy: float) -> Optional[str]:
        """记录测验尝试"""
        details = {
            'quiz_id': quiz_id,
            'quiz_title': quiz_title,
            'score': score,
            'accuracy': accuracy
        }
        return cls.create_log(user_id, nickname, 'quiz_attempt', details)

    @classmethod
    def log_learning_progress(cls, user_id: int, nickname: str, content_type: str,
                             content_id: int, action: str) -> Optional[str]:
        """记录学习进度"""
        details = {
            'content_type': content_type,  # vocab, grammar, listening
            'content_id': content_id,
            'action': action  # started, completed, reviewed
        }
        return cls.create_log(user_id, nickname, 'learning_progress', details)

    @classmethod
    def log_post_creation(cls, user_id: int, nickname: str, post_id: int,
                         post_title: str, category: str) -> Optional[str]:
        """记录帖子创建"""
        details = {
            'post_id': post_id,
            'post_title': post_title,
            'category': category
        }
        return cls.create_log(user_id, nickname, 'post_created', details)

    @classmethod
    def log_comment_creation(cls, user_id: int, nickname: str, post_id: int,
                           comment_id: int) -> Optional[str]:
        """记录评论创建"""
        details = {
            'post_id': post_id,
            'comment_id': comment_id
        }
        return cls.create_log(user_id, nickname, 'comment_created', details)

    @classmethod
    def log_admin_action(cls, user_id: int, nickname: str, action: str,
                        target_type: str, target_id: int, details_info: Dict = None) -> Optional[str]:
        """记录管理员操作"""
        details = {
            'action': action,  # approve, reject, delete, update
            'target_type': target_type,  # post, user, content
            'target_id': target_id
        }
        if details_info:
            details.update(details_info)

        return cls.create_log(user_id, nickname, 'admin_action', details)