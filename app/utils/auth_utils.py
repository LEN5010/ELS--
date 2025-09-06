import secrets
import jwt
from datetime import datetime, timedelta
from flask import current_app
from app.utils.db import get_db_cursor

def generate_salt():
    """生成16字符的盐值"""
    return secrets.token_hex(8)

def hash_password(password, salt):
    """调用MySQL存储函数进行密码哈希"""
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT hash_password(%s, %s) as pwd_hash", (password, salt))
        result = cursor.fetchone()
        return result['pwd_hash']

def generate_token(user_id):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None