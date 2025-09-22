from pymongo import MongoClient
from contextlib import contextmanager
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        """获取MongoDB客户端"""
        if cls._client is None:
            try:
                cls._client = MongoClient(Config.MONGO_URI)
                # 测试连接
                cls._client.admin.command('ping')
                logger.info("MongoDB连接成功")
            except Exception as e:
                logger.error(f"MongoDB连接失败: {e}")
                raise e
        return cls._client

    @classmethod
    def get_database(cls):
        """获取数据库实例"""
        if cls._db is None:
            client = cls.get_client()
            cls._db = client.get_database()
        return cls._db

    @classmethod
    def close_connection(cls):
        """关闭连接"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None

@contextmanager
def get_mongo_collection(collection_name):
    """获取MongoDB集合的上下文管理器"""
    try:
        db = MongoDB.get_database()
        collection = db[collection_name]
        yield collection
    except Exception as e:
        logger.error(f"获取MongoDB集合失败: {e}")
        raise e