from flask import Blueprint, request, jsonify
from app.utils.db import get_db_cursor
from app.schemas.response import success_response, error_response

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/vocab', methods=['GET'])
def get_vocab_list():
    """获取词汇列表"""
    level = request.args.get('level', 'A1')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    
    try:
        with get_db_cursor(commit=False) as cursor:
            # 获取总数
            cursor.execute("SELECT COUNT(*) as total FROM vocab WHERE level = %s", (level,))
            total = cursor.fetchone()['total']
            
            # 获取词汇列表
            cursor.execute("""
                SELECT word_id, word, meaning, example, level
                FROM vocab
                WHERE level = %s
                LIMIT %s OFFSET %s
            """, (level, per_page, offset))
            
            vocab_list = cursor.fetchall()
            
            return jsonify(success_response({
                "total": total,
                "page": page,
                "per_page": per_page,
                "data": vocab_list
            }))
            
    except Exception as e:
        return error_response(f"获取词汇列表失败: {str(e)}", 500)

@learning_bp.route('/grammar', methods=['GET'])
def get_grammar_list():
    """获取语法教程列表"""
    level = request.args.get('level', 'A1')
    
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT grammar_id, title, content, level
                FROM grammar
                WHERE level = %s
            """, (level,))
            
            grammar_list = cursor.fetchall()
            
            return jsonify(success_response(grammar_list))
            
    except Exception as e:
        return error_response(f"获取语法列表失败: {str(e)}", 500)

@learning_bp.route('/listening', methods=['GET'])
def get_listening_list():
    """获取听力材料列表"""
    level = request.args.get('level', 'A1')
    
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT listen_id, title, audio_url, transcript, level
                FROM listening
                WHERE level = %s
            """, (level,))
            
            listening_list = cursor.fetchall()
            
            return jsonify(success_response(listening_list))
            
    except Exception as e:
        return error_response(f"获取听力列表失败: {str(e)}", 500)