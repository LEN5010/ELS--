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
                "community": "/api/community",
                "admin": "/api/admin",  # 添加管理员端点
                "logs": "/api/logs"     # 添加日志端点
            }
        })
    
    # 健康检查
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "service": "English Learning System"})
    
    # 注册蓝图
    from app.routes import auth_bp, user_bp, learning_bp, quiz_bp, community_bp
    from app.routes.admin import admin_bp  # 导入管理员蓝图
    from app.routes.logs import logs_bp   # 导入日志蓝图

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')  # 注册管理员路由
    app.register_blueprint(logs_bp, url_prefix='/api/logs')    # 注册日志路由
    
    return app