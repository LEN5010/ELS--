from flask import Blueprint, request, jsonify
from app.utils.db import get_db_cursor
from app.schemas.response import success_response, error_response
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/list', methods=['GET'])
def get_quiz_list():
    """获取测验列表"""
    quiz_type = request.args.get('type')
    
    try:
        with get_db_cursor(commit=False) as cursor:
            if quiz_type:
                cursor.execute("""
                    SELECT quiz_id, quiz_type, title, total_points
                    FROM quiz
                    WHERE quiz_type = %s
                """, (quiz_type,))
            else:
                cursor.execute("""
                    SELECT quiz_id, quiz_type, title, total_points
                    FROM quiz
                """)
            
            quiz_list = cursor.fetchall()
            
            return jsonify(success_response(quiz_list))
            
    except Exception as e:
        return error_response(f"获取测验列表失败: {str(e)}", 500)

@quiz_bp.route('/<int:quiz_id>/questions', methods=['GET'])
def get_quiz_questions(quiz_id):
    """获取测验题目"""
    try:
        with get_db_cursor(commit=False) as cursor:
            # 获取测验信息
            cursor.execute("""
                SELECT quiz_id, quiz_type, title, total_points
                FROM quiz
                WHERE quiz_id = %s
            """, (quiz_id,))
            
            quiz_info = cursor.fetchone()
            if not quiz_info:
                return error_response("测验不存在", 404)
            
            # 获取题目列表
            cursor.execute("""
                SELECT question_id, question, option_a, option_b, 
                       option_c, option_d, score
                FROM quiz_question
                WHERE quiz_id = %s
            """, (quiz_id,))
            
            questions = cursor.fetchall()
            
            return jsonify(success_response({
                "quiz": quiz_info,
                "questions": questions
            }))
            
    except Exception as e:
        return error_response(f"获取测验题目失败: {str(e)}", 500)

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    """提交测验答案"""
    data = request.get_json()
    user_id = data.get('user_id')
    answers = data.get('answers', {})  # {question_id: selected_option}
    
    if not user_id:
        return error_response("用户ID不能为空")
    
    try:
        with get_db_cursor() as cursor:
            