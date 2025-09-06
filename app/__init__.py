from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from app.routes import auth_bp, user_bp, learning_bp, quiz_bp, community_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    
    return app