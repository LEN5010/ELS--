from flask import Blueprint, request, jsonify
from app.utils.db import get_db_cursor
from app.utils.auth_utils import generate_salt, hash_password, generate_token
from app.schemas.response import success_response, error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname', email.split('@')[0])
    
    if not email or not password:
        return error_response("邮箱和密码不能为空")
    
    try:
        with get_db_cursor() as cursor:
            # 检查邮箱是否已存在
            cursor.execute("SELECT user_id FROM user_auth WHERE email = %s", (email,))
            if cursor.fetchone():
                return error_response("邮箱已被注册")
            
            # 生成盐值和密码哈希
            salt = generate_salt()
            pwd_hash = hash_password(password, salt)
            
            # 插入用户认证信息
            cursor.execute("""
                INSERT INTO user_auth (email, pwd_hash, salt) 
                VALUES (%s, %s, %s)
            """, (email, pwd_hash, salt))
            
            user_id = cursor.lastrowid
            
            # 插入用户基本信息
            cursor.execute("""
                INSERT INTO user_profile (user_id, nickname) 
                VALUES (%s, %s)
            """, (user_id, nickname))
            
            # 初始化学习进度
            cursor.execute("""
                INSERT INTO progress (user_id) VALUES (%s)
            """, (user_id,))
            
            # 生成token
            token = generate_token(user_id)
            
            return jsonify(success_response({
                "token": token,
                "user_id": user_id,
                "email": email,
                "nickname": nickname
            }, "注册成功"))
            
    except Exception as e:
        return error_response(f"注册失败: {str(e)}", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return error_response("邮箱和密码不能为空")
    
    try:
        with get_db_cursor(commit=False) as cursor:
            # 获取用户认证信息
            cursor.execute("""
                SELECT ua.user_id, ua.pwd_hash, ua.salt, up.nickname, up.role
                FROM user_auth ua
                JOIN user_profile up ON ua.user_id = up.user_id
                WHERE ua.email = %s
            """, (email,))
            
            user = cursor.fetchone()
            if not user:
                return error_response("用户不存在")
            
            # 验证密码
            pwd_hash = hash_password(password, user['salt'])
            if pwd_hash != user['pwd_hash']:
                return error_response("密码错误")
            
            # 生成token
            token = generate_token(user['user_id'])
            
            return jsonify(success_response({
                "token": token,
                "user_id": user['user_id'],
                "email": email,
                "nickname": user['nickname'],
                "role": user['role']
            }, "登录成功"))
            
    except Exception as e:
        return error_response(f"登录失败: {str(e)}", 500)