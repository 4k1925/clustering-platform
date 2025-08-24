import os
from flask import Flask, request
from .config import Config
from app.extensions import db, migrate, login_manager, jwt, cors
from app.utils.helpers import ensure_upload_folder
def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
        app.logger.info(f"创建上传文件夹: {upload_folder}")
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
    from app.routes.admin import admin_bp
        
        # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(clustering_bp, url_prefix='/api/clustering')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')  # 确保这行执行
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
         
def configure_cors(app):
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173"],  # 确保与前端端口一致
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "expose_headers": ["Content-Disposition"],
            }
        }
    )

    @app.before_request
    def handle_options():
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            return response