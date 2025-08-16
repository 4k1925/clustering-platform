import os
from flask import Flask
from .config import Config
from app.extensions import db, migrate, login_manager, jwt, cors

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    initialize_extensions(app)
    # 注册蓝图
    register_blueprints(app)
    # 配置CORS
    configure_cors(app)
    
    return app

def initialize_extensions(app):
    """初始化Flask扩展"""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    
    # 配置登录管理器
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

def register_blueprints(app):
    """注册所有蓝图"""
    from app.routes.auth import auth_bp
    from app.routes.clustering import clustering_bp
    from app.routes.student import student_bp
    from app.routes.teacher import teacher_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(clustering_bp, url_prefix='/api/clustering')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')

def configure_cors(app):
    cors.init_app(
        app,
        resources={
            r"/*": {
                "origins": ["http://localhost:5173"],  # 确保与前端端口一致
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "expose_headers": ["Content-Disposition"],
            }
        }
    )