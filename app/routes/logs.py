from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timezone, timedelta
from app.utils.db import get_db_cursor
from app.utils.auth_utils import verify_token
from app.models.activity_log import ActivityLog
from app.schemas.response import success_response, error_response

logs_bp = Blueprint('logs', __name__)

def auth_required(f):
    """身份验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return error_response("未授权访问", 401)

        # 获取用户信息
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT nickname, role FROM user_profile WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()

            if not user:
                return error_response("用户不存在", 404)

        request.current_user = {
            'user_id': user_id,
            'nickname': user['nickname'],
            'role': user['role']
        }
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @auth_required
    def decorated_function(*args, **kwargs):
        if request.current_user['role'] != 'admin':
            return error_response("需要管理员权限", 403)
        return f(*args, **kwargs)
    return decorated_function

@logs_bp.route('/my-logs', methods=['GET'])
@auth_required
def get_my_logs():
    """获取当前用户的活动日志"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        skip = (page - 1) * per_page

        user_id = request.current_user['user_id']
        logs = ActivityLog.get_user_logs(user_id, limit=per_page, skip=skip)

        return jsonify(success_response({
            'logs': logs,
            'page': page,
            'per_page': per_page
        }))

    except Exception as e:
        return error_response(f"获取活动日志失败: {str(e)}", 500)

@logs_bp.route('/user/<int:user_id>/logs', methods=['GET'])
@admin_required
def get_user_logs(user_id):
    """管理员获取指定用户的活动日志"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        skip = (page - 1) * per_page

        logs = ActivityLog.get_user_logs(user_id, limit=per_page, skip=skip)

        return jsonify(success_response({
            'logs': logs,
            'page': page,
            'per_page': per_page,
            'user_id': user_id
        }))

    except Exception as e:
        return error_response(f"获取用户活动日志失败: {str(e)}", 500)

@logs_bp.route('/by-action/<action_type>', methods=['GET'])
@admin_required
def get_logs_by_action(action_type):
    """根据操作类型获取日志"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        skip = (page - 1) * per_page

        logs = ActivityLog.get_logs_by_action_type(action_type, limit=per_page, skip=skip)

        return jsonify(success_response({
            'logs': logs,
            'action_type': action_type,
            'page': page,
            'per_page': per_page
        }))

    except Exception as e:
        return error_response(f"获取操作日志失败: {str(e)}", 500)

@logs_bp.route('/by-date-range', methods=['GET'])
@admin_required
def get_logs_by_date_range():
    """根据日期范围获取日志"""
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        user_id = request.args.get('user_id', type=int)
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        skip = (page - 1) * per_page

        # 解析日期
        try:
            start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
            end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        except ValueError:
            return error_response("日期格式错误，请使用ISO格式 (YYYY-MM-DD或YYYY-MM-DDTHH:MM:SS)", 400)

        if not start_date and not end_date:
            return error_response("至少需要提供开始日期或结束日期", 400)

        logs = ActivityLog.get_logs_by_date_range(
            start_date, end_date, user_id, limit=per_page, skip=skip
        )

        return jsonify(success_response({
            'logs': logs,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'user_id': user_id,
            'page': page,
            'per_page': per_page
        }))

    except Exception as e:
        return error_response(f"获取日期范围日志失败: {str(e)}", 500)

@logs_bp.route('/statistics', methods=['GET'])
@admin_required
def get_log_statistics():
    """获取日志统计信息"""
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date = None
        end_date = None

        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except ValueError:
                return error_response("开始日期格式错误", 400)

        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
            except ValueError:
                return error_response("结束日期格式错误", 400)

        stats = ActivityLog.get_statistics(start_date, end_date)

        return jsonify(success_response(stats))

    except Exception as e:
        return error_response(f"获取日志统计失败: {str(e)}", 500)

@logs_bp.route('/create', methods=['POST'])
@auth_required
def create_log():
    """手动创建日志（主要用于测试）"""
    try:
        data = request.get_json()
        action_type = data.get('action_type')
        details = data.get('details', {})

        if not action_type:
            return error_response("操作类型不能为空", 400)

        user_id = request.current_user['user_id']
        nickname = request.current_user['nickname']

        log_id = ActivityLog.create_log(user_id, nickname, action_type, details)

        if log_id:
            return jsonify(success_response({
                'log_id': log_id
            }, "日志创建成功"))
        else:
            return error_response("日志创建失败", 500)

    except Exception as e:
        return error_response(f"创建日志失败: {str(e)}", 500)

# 以下是一些便捷的日志记录接口

@logs_bp.route('/log-quiz-attempt', methods=['POST'])
@auth_required
def log_quiz_attempt():
    """记录测验尝试"""
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        quiz_title = data.get('quiz_title')
        score = data.get('score')
        accuracy = data.get('accuracy')

        if not all([quiz_id, quiz_title, score is not None, accuracy is not None]):
            return error_response("缺少必要参数", 400)

        user_id = request.current_user['user_id']
        nickname = request.current_user['nickname']

        log_id = ActivityLog.log_quiz_attempt(
            user_id, nickname, quiz_id, quiz_title, score, accuracy
        )

        if log_id:
            return jsonify(success_response({'log_id': log_id}, "测验日志记录成功"))
        else:
            return error_response("测验日志记录失败", 500)

    except Exception as e:
        return error_response(f"记录测验日志失败: {str(e)}", 500)

@logs_bp.route('/log-learning-progress', methods=['POST'])
@auth_required
def log_learning_progress():
    """记录学习进度"""
    try:
        data = request.get_json()
        content_type = data.get('content_type')  # vocab, grammar, listening
        content_id = data.get('content_id')
        action = data.get('action')  # started, completed, reviewed

        if not all([content_type, content_id, action]):
            return error_response("缺少必要参数", 400)

        if content_type not in ['vocab', 'grammar', 'listening']:
            return error_response("无效的内容类型", 400)

        if action not in ['started', 'completed', 'reviewed']:
            return error_response("无效的操作类型", 400)

        user_id = request.current_user['user_id']
        nickname = request.current_user['nickname']

        log_id = ActivityLog.log_learning_progress(
            user_id, nickname, content_type, content_id, action
        )

        if log_id:
            return jsonify(success_response({'log_id': log_id}, "学习进度日志记录成功"))
        else:
            return error_response("学习进度日志记录失败", 500)

    except Exception as e:
        return error_response(f"记录学习进度日志失败: {str(e)}", 500)

@logs_bp.route('/recent-activities', methods=['GET'])
@auth_required
def get_recent_activities():
    """获取最近的活动（用于仪表板显示）"""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)

        if request.current_user['role'] == 'admin':
            # 管理员可以看到所有用户的最近活动
            # 获取最近7天的活动
            start_date = datetime.now(timezone.utc) - timedelta(days=7)
            logs = ActivityLog.get_logs_by_date_range(
                start_date=start_date,
                end_date=datetime.now(timezone.utc),
                limit=limit
            )
        else:
            # 普通用户只能看到自己的活动
            user_id = request.current_user['user_id']
            logs = ActivityLog.get_user_logs(user_id, limit=limit)

        return jsonify(success_response({
            'recent_activities': logs,
            'limit': limit
        }))

    except Exception as e:
        return error_response(f"获取最近活动失败: {str(e)}", 500)