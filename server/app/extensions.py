from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
cors = CORS()

@login_manager.unauthorized_handler
def unauthorized_handler():
    from flask import request, jsonify
    if request.path.startswith('/api/'):
        return jsonify({'error': '请先登录'}), 401
