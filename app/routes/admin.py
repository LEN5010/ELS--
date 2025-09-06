from flask import Blueprint, request, jsonify
from functools import wraps
from app.utils.db import get_db_cursor
from app.utils.auth_utils import verify_token
from app.schemas.response import success_response, error_response

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return error_response("未授权访问", 401)
        
        # 检查是否是管理员
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT role FROM user_profile WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()
            
            if not user or user['role'] != 'admin':
                return error_response("需要管理员权限", 403)
        
        return f(*args, **kwargs)
    return decorated_function

# 1. 用户管理
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """获取所有用户列表"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    
    try:
        with get_db_cursor(commit=False) as cursor:
            # 获取总数
            cursor.execute("SELECT COUNT(*) as total FROM user_auth")
            total = cursor.fetchone()['total']
            
            # 获取用户列表
            cursor.execute("""
                SELECT ua.user_id, ua.email, ua.created_at,
                       up.nickname, up.gender, up.role,
                       p.vocab_learned, p.grammar_learned, p.listening_done
                FROM user_auth ua
                JOIN user_profile up ON ua.user_id = up.user_id
                LEFT JOIN progress p ON ua.user_id = p.user_id
                ORDER BY ua.created_at DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            
            users = cursor.fetchall()
            
            return jsonify(success_response({
                "total": total,
                "page": page,
                "per_page": per_page,
                "data": users
            }))
            
    except Exception as e:
        return error_response(f"获取用户列表失败: {str(e)}", 500)

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """更新用户角色"""
    data = request.get_json()
    role = data.get('role')
    
    if role not in ['student', 'admin']:
        return error_response("无效的角色")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE user_profile SET role = %s WHERE user_id = %s
            """, (role, user_id))
            
            return jsonify(success_response(None, "角色更新成功"))
            
    except Exception as e:
        return error_response(f"更新角色失败: {str(e)}", 500)

# 2. 内容审核
@admin_bp.route('/posts/pending', methods=['GET'])
@admin_required
def get_pending_posts():
    """获取待审核的帖子"""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT p.*, up.nickname
                FROM post p
                JOIN user_profile up ON p.user_id = up.user_id
                WHERE p.status = 'pending'
                ORDER BY p.created_at DESC
            """)
            
            posts = cursor.fetchall()
            
            return jsonify(success_response(posts))
            
    except Exception as e:
        return error_response(f"获取待审核帖子失败: {str(e)}", 500)

@admin_bp.route('/posts/<int:post_id>/review', methods=['PUT'])
@admin_required
def review_post(post_id):
    """审核帖子"""
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['approved', 'rejected']:
        return error_response("无效的审核状态")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE post SET status = %s WHERE post_id = %s
            """, (status, post_id))
            
            return jsonify(success_response(None, "审核完成"))
            
    except Exception as e:
        return error_response(f"审核失败: {str(e)}", 500)

# 3. 学习资源管理
@admin_bp.route('/vocab', methods=['POST'])
@admin_required
def add_vocab():
    """添加词汇"""
    data = request.get_json()
    
    required_fields = ['word', 'meaning', 'level']
    if not all(field in data for field in required_fields):
        return error_response("缺少必要字段")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO vocab (word, meaning, example, level)
                VALUES (%s, %s, %s, %s)
            """, (data['word'], data['meaning'], 
                  data.get('example', ''), data['level']))
            
            word_id = cursor.lastrowid
            
            return jsonify(success_response({
                "word_id": word_id
            }, "词汇添加成功"))
            
    except Exception as e:
        return error_response(f"添加词汇失败: {str(e)}", 500)

@admin_bp.route('/vocab/<int:word_id>', methods=['PUT'])
@admin_required
def update_vocab(word_id):
    """更新词汇"""
    data = request.get_json()
    
    update_fields = []
    params = []
    
    for field in ['word', 'meaning', 'example', 'level']:
        if field in data:
            update_fields.append(f"{field} = %s")
            params.append(data[field])
    
    if not update_fields:
        return error_response("没有要更新的字段")
    
    params.append(word_id)
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute(f"""
                UPDATE vocab SET {', '.join(update_fields)}
                WHERE word_id = %s
            """, params)
            
            return jsonify(success_response(None, "词汇更新成功"))
            
    except Exception as e:
        return error_response(f"更新词汇失败: {str(e)}", 500)

@admin_bp.route('/vocab/<int:word_id>', methods=['DELETE'])
@admin_required
def delete_vocab(word_id):
    """删除词汇"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM vocab WHERE word_id = %s", (word_id,))
            
            return jsonify(success_response(None, "词汇删除成功"))
            
    except Exception as e:
        return error_response(f"删除词汇失败: {str(e)}", 500)

# 类似的方法可以用于grammar和listening的增删改

@admin_bp.route('/grammar', methods=['POST'])
@admin_required
def add_grammar():
    """添加语法教程"""
    data = request.get_json()
    
    required_fields = ['title', 'content', 'level']
    if not all(field in data for field in required_fields):
        return error_response("缺少必要字段")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO grammar (title, content, level)
                VALUES (%s, %s, %s)
            """, (data['title'], data['content'], data['level']))
            
            grammar_id = cursor.lastrowid
            
            return jsonify(success_response({
                "grammar_id": grammar_id
            }, "语法教程添加成功"))
            
    except Exception as e:
        return error_response(f"添加语法教程失败: {str(e)}", 500)

@admin_bp.route('/listening', methods=['POST'])
@admin_required
def add_listening():
    """添加听力材料"""
    data = request.get_json()
    
    required_fields = ['title', 'audio_url', 'level']
    if not all(field in data for field in required_fields):
        return error_response("缺少必要字段")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO listening (title, audio_url, transcript, level)
                VALUES (%s, %s, %s, %s)
            """, (data['title'], data['audio_url'], 
                  data.get('transcript', ''), data['level']))
            
            listen_id = cursor.lastrowid
            
            return jsonify(success_response({
                "listen_id": listen_id
            }, "听力材料添加成功"))
            
    except Exception as e:
        return error_response(f"添加听力材料失败: {str(e)}", 500)

# 4. 测验管理
@admin_bp.route('/quiz', methods=['POST'])
@admin_required
def create_quiz():
    """创建测验"""
    data = request.get_json()
    
    required_fields = ['quiz_type', 'title', 'total_points']
    if not all(field in data for field in required_fields):
        return error_response("缺少必要字段")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO quiz (quiz_type, title, total_points)
                VALUES (%s, %s, %s)
            """, (data['quiz_type'], data['title'], data['total_points']))
            
            quiz_id = cursor.lastrowid
            
            return jsonify(success_response({
                "quiz_id": quiz_id
            }, "测验创建成功"))
            
    except Exception as e:
        return error_response(f"创建测验失败: {str(e)}", 500)

@admin_bp.route('/quiz/<int:quiz_id>/questions', methods=['POST'])
@admin_required
def add_quiz_question(quiz_id):
    """添加测验题目"""
    data = request.get_json()
    
    required_fields = ['question', 'option_a', 'option_b', 
                      'option_c', 'option_d', 'correct_opt', 'score']
    if not all(field in data for field in required_fields):
        return error_response("缺少必要字段")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO quiz_question 
                (quiz_id, question, option_a, option_b, option_c, 
                 option_d, correct_opt, score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (quiz_id, data['question'], data['option_a'], 
                  data['option_b'], data['option_c'], data['option_d'],
                  data['correct_opt'], data['score']))
            
            question_id = cursor.lastrowid
            
            return jsonify(success_response({
                "question_id": question_id
            }, "题目添加成功"))
            
    except Exception as e:
        return error_response(f"添加题目失败: {str(e)}", 500)

# 5. 数据统计
@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics():
    """获取系统统计数据"""
    try:
        with get_db_cursor(commit=False) as cursor:
            stats = {}
            
            # 用户统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
                    SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as student_count
                FROM user_profile
            """)
            stats['users'] = cursor.fetchone()
            
            # 学习资源统计
            cursor.execute("SELECT COUNT(*) as total FROM vocab")
            stats['vocab_count'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM grammar")
            stats['grammar_count'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM listening")
            stats['listening_count'] = cursor.fetchone()['total']
            
            # 测验统计
            cursor.execute("SELECT COUNT(*) as total FROM quiz")
            stats['quiz_count'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM quiz_result")
            stats['quiz_attempts'] = cursor.fetchone()['total']
            
            # 社区统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_posts,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_posts,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_posts
                FROM post
            """)
            stats['posts'] = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as total FROM comment")
            stats['comment_count'] = cursor.fetchone()['total']
            
            # 今日新增用户
            cursor.execute("""
                SELECT COUNT(*) as today_users 
                FROM user_auth 
                WHERE DATE(created_at) = CURDATE()
            """)
            stats['today_users'] = cursor.fetchone()['today_users']
            
            return jsonify(success_response(stats))
            
    except Exception as e:
        return error_response(f"获取统计数据失败: {str(e)}", 500)

@admin_bp.route('/statistics/quiz-performance', methods=['GET'])
@admin_required
def get_quiz_performance():
    """获取测验成绩统计"""
    try:
        with get_db_cursor(commit=False) as cursor:
                        # 各测验的平均分和参与人数
            cursor.execute("""
                SELECT 
                    q.quiz_id,
                    q.title,
                    q.quiz_type,
                    COUNT(qr.result_id) as attempt_count,
                    AVG(qr.score) as avg_score,
                    MAX(qr.score) as max_score,
                    MIN(qr.score) as min_score
                FROM quiz q
                LEFT JOIN quiz_result qr ON q.quiz_id = qr.quiz_id
                GROUP BY q.quiz_id
                ORDER BY attempt_count DESC
            """)
            
            quiz_stats = cursor.fetchall()
            
            # 使用MySQL函数计算各测验的平均准确率
            for stat in quiz_stats:
                if stat['attempt_count'] > 0:
                    cursor.execute("""
                        SELECT AVG(fn_calc_accuracy(correct_cnt, total_cnt)) as avg_accuracy
                        FROM quiz_result
                        WHERE quiz_id = %s
                    """, (stat['quiz_id'],))
                    
                    accuracy_result = cursor.fetchone()
                    stat['avg_accuracy'] = float(accuracy_result['avg_accuracy']) if accuracy_result['avg_accuracy'] else 0
                else:
                    stat['avg_accuracy'] = 0
            
            return jsonify(success_response(quiz_stats))
            
    except Exception as e:
        return error_response(f"获取测验成绩统计失败: {str(e)}", 500)

@admin_bp.route('/statistics/user-progress', methods=['GET'])
@admin_required
def get_user_progress_stats():
    """获取用户学习进度统计"""
    try:
        with get_db_cursor(commit=False) as cursor:
            # 学习进度分布
            cursor.execute("""
                SELECT 
                    AVG(vocab_learned) as avg_vocab,
                    AVG(grammar_learned) as avg_grammar,
                    AVG(listening_done) as avg_listening,
                    MAX(vocab_learned) as max_vocab,
                    MAX(grammar_learned) as max_grammar,
                    MAX(listening_done) as max_listening
                FROM progress
            """)
            
            progress_stats = cursor.fetchone()
            
            # 活跃用户（最近7天有学习记录）
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as active_users
                FROM progress
                WHERE last_update >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            
            active_users = cursor.fetchone()['active_users']
            progress_stats['active_users_7days'] = active_users
            
            return jsonify(success_response(progress_stats))
            
    except Exception as e:
        return error_response(f"获取用户进度统计失败: {str(e)}", 500)