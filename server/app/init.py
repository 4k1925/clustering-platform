# 初始化Flask应用
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# 修改create_app函数
def create_app(config_class='config.Config'):  # 注意大小写
    app = Flask(__name__)  # 修正Flask大写
    app.config.from_object(config_class)
    
    # 延迟导入蓝图（解决循环依赖）
    with app.app_context():
        from .routes.auth import auth_bp
        from .routes.clustering import clustering_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(clustering_bp)
    
    return app  # 缩进修正