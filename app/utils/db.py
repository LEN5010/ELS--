import pymysql
from contextlib import contextmanager
from app.config import Config

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    connection = None
    try:
        connection = pymysql.connect(**Config.DB_CONFIG)
        yield connection
    finally:
        if connection:
            connection.close()

@contextmanager
def get_db_cursor(commit=True):
    """获取数据库游标的上下文管理器"""
    with get_db_connection() as connection:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()