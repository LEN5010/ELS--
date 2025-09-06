import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_salt():
    """生成16字符的盐值"""
    return secrets.token_hex(8)

def hash_password(password, salt):
    """密码哈希函数"""
    return hashlib.sha256((password + salt).encode()).hexdigest().upper()

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