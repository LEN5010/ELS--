from flask import Blueprint, request, jsonify
from app.utils.db import get_db_cursor
from app.schemas.response import success_response, error_response

community_bp = Blueprint('community', __name__)

@community_bp.route('/posts', methods=['GET'])
def get_posts():
    """获取帖子列表"""
    category = request.args.get('category')
    status = request.args.get('status', 'approved')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    
    try:
        with get_db_cursor(commit=False) as cursor:
            # 构建查询条件
            conditions = ["p.status = %s"]
            params = [status]
            
            if category:
                conditions.append("p.category = %s")
                params.append(category)
            
            where_clause = " AND ".join(conditions)
            
            # 获取总数
            cursor.execute(f"""
                SELECT COUNT(*) as total 
                FROM post p 
                WHERE {where_clause}
            """, params)
            total = cursor.fetchone()['total']
            
            # 获取帖子列表
            params.extend([per_page, offset])
            cursor.execute(f"""
                SELECT p.*, up.nickname,
                       (SELECT COUNT(*) FROM comment WHERE post_id = p.post_id) as comment_count
                FROM post p
                JOIN user_profile up ON p.user_id = up.user_id
                WHERE {where_clause}
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """, params)
            
            posts = cursor.fetchall()
            
            return jsonify(success_response({
                "total": total,
                "page": page,
                "per_page": per_page,
                "data": posts
            }))
            
    except Exception as e:
        return error_response(f"获取帖子列表失败: {str(e)}", 500)

@community_bp.route('/posts', methods=['POST'])
def create_post():
    """创建帖子"""
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    category = data.get('category', 'general')
    
    if not all([user_id, title, content]):
        return error_response("用户ID、标题和内容不能为空")
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO post (user_id, title, content, category)
                VALUES (%s, %s, %s, %s)
            """, (user_id, title, content, category))
            
            post_id = cursor.lastrowid
            
            return jsonify(success_response({
                "post_id": post_id
            }, "帖子创建成功"))
            
    except Exception as e:
        return error_response(f"创建帖子失败: {str(e)}", 500)

@community_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    """获取帖子详情"""
    try:
        with get_db_cursor(commit=False) as cursor:
            # 获取帖子信息
            cursor.execute("""
                SELECT p.*, up.nickname
                FROM post p
                JOIN user_profile up ON p.user_id = up.user_id
                WHERE p.post_id = %s AND p.status = 'approved'
            """, (post_id,))
            
            post = cursor.fetchone()
            if not post:
                return error_response("帖子不存在", 404)
            
            # 获取评论列表
            cursor.execute("""
                SELECT c.*, up.nickname
                FROM comment c
                JOIN user_profile up ON c.user_id = up.user_id
                WHERE c.post_id = %s
                ORDER BY c.created_at ASC
            """, (post_id,))
            
            comments = cursor.fetchall()
            
            return jsonify(success_response({
                "post": post,
                "comments": comments
            }))
            
    except Exception as e:
        return error_response(f"获取帖子详情失败: {str(e)}", 500)

@community_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    """创建评论"""
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')
    
    if not all([user_id, content]):
        return error_response("用户ID和内容不能为空")
    
    try:
        with get_db_cursor() as cursor:
            # 检查帖子是否存在
            cursor.execute("SELECT post_id FROM post WHERE post_id = %s", (post_id,))
            if not cursor.fetchone():
                return error_response("帖子不存在", 404)
            
            # 插入评论
            cursor.execute("""
                INSERT INTO comment (post_id, user_id, content)
                VALUES (%s, %s, %s)
            """, (post_id, user_id, content))
            
            comment_id = cursor.lastrowid
            
            return jsonify(success_response({
                "comment_id": comment_id
            }, "评论成功"))
            
    except Exception as e:
        return error_response(f"创建评论失败: {str(e)}", 500)