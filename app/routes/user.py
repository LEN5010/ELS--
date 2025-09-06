from flask import Blueprint, request, jsonify
from app.utils.db import get_db_cursor
from app.schemas.response import success_response, error_response

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """获取用户信息"""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT up.*, ua.email
                FROM user_profile up
                JOIN user_auth ua ON up.user_id = ua.user_id
                WHERE up.user_id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            if not user:
                return error_response("用户不存在", 404)
            
            return jsonify(success_response(user))
            
    except Exception as e:
        return error_response(f"获取用户信息失败: {str(e)}", 500)

@user_bp.route('/profile/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """更新用户信息"""
    data = request.get_json()
    
    try:
        with get_db_cursor() as cursor:
            # 构建更新语句
            update_fields = []
            params = []
            
            if 'nickname' in data:
                update_fields.append("nickname = %s")
                params.append(data['nickname'])
            
            if 'gender' in data:
                update_fields.append("gender = %s")
                params.append(data['gender'])
            
            if 'birthday' in data:
                update_fields.append("birthday = %s")
                params.append(data['birthday'])
            
            if 'myps' in data:
                update_fields.append("myps = %s")
                params.append(data['myps'])
            
            if not update_fields:
                return error_response("没有要更新的字段")
            
            params.append(user_id)
            
            cursor.execute(f"""
                UPDATE user_profile 
                SET {', '.join(update_fields)}
                WHERE user_id = %s
            """, params)
            
            return jsonify(success_response(None, "更新成功"))
            
    except Exception as e:
        return error_response(f"更新用户信息失败: {str(e)}", 500)

@user_bp.route('/progress/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    """获取用户学习进度"""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT * FROM progress WHERE user_id = %s
            """, (user_id,))
            
            progress = cursor.fetchone()
            if not progress:
                return error_response("进度信息不存在", 404)
            
            # 获取测验历史
            cursor.execute("""
                SELECT qr.*, q.title, q.quiz_type
                FROM quiz_result qr
                JOIN quiz q ON qr.quiz_id = q.quiz_id
                WHERE qr.user_id = %s
                ORDER BY qr.taken_at DESC
                LIMIT 10
            """, (user_id,))
            
            quiz_history = cursor.fetchall()
            
            return jsonify(success_response({
                "progress": progress,
                "quiz_history": quiz_history
            }))
            
    except Exception as e:
        return error_response(f"获取学习进度失败: {str(e)}", 500)

@user_bp.route('/progress/<int:user_id>', methods=['PUT'])
def update_user_progress(user_id):
    """更新用户学习进度"""
    data = request.get_json()
    progress_type = data.get('type')  # vocab, grammar, listening
    increment = data.get('increment', 1)
    
    if progress_type not in ['vocab', 'grammar', 'listening']:
        return error_response("无效的进度类型")
    
    try:
        with get_db_cursor() as cursor:
            field_map = {
                'vocab': 'vocab_learned',
                'grammar': 'grammar_learned',
                'listening': 'listening_done'
            }
            
            field = field_map[progress_type]
            
            cursor.execute(f"""
                UPDATE progress 
                SET {field} = {field} + %s,
                    last_update = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (increment, user_id))
            
            return jsonify(success_response(None, "进度更新成功"))
            
    except Exception as e:
        return error_response(f"更新进度失败: {str(e)}", 500)