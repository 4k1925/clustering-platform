import os
from flask import Flask, request
from .config import Config
from app.extensions import db, migrate, login_manager, jwt, cors
from app.utils.helpers import ensure_upload_folder
from app.models.user import User  # 在这里导入 User
from .import models

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
    
    # 配置 JWT 用户查找回调（新增）
    configure_jwt_callbacks(app)
    upload_dir = os.path.join(app.root_path, 'uploads', 'reports')
    os.makedirs(upload_dir, exist_ok=True)
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
    
    # 配置 login_manager 的用户加载器
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

def configure_jwt_callbacks(app):
    """配置 JWT 回调函数（新增）"""
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """JWT 用户查找回调"""
        identity = jwt_data["sub"]
        return User.query.filter_by(user_id=int(identity)).first()

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
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
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