from flask import Flask
from .extensions import db, migrate, login_manager
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 延迟导入路由（避免循环导入）
    with app.app_context():
        from .routes.auth import auth_bp
        from .routes.clustering import clustering_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(clustering_bp)
    
    return app