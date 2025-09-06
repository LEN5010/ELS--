from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 添加根路径
    @app.route('/')
    def index():
        return jsonify({
            "message": "English Learning System API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth",
                "user": "/api/user",
                "learning": "/api/learning",
                "quiz": "/api/quiz",
                "community": "/api/community"
            }
        })
    
    # 健康检查
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "service": "English Learning System"})
    
    # 注册蓝图
    from app.routes import auth_bp, user_bp, learning_bp, quiz_bp, community_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    
    return app