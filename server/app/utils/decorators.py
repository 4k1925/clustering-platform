# server/app/utils/decorators.py
from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def validate_json(required_fields):
    """简化版JSON验证装饰器（仅检查字段存在性）"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing JSON data"}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Login required'}), 403
            if current_user.role != role_name:
                return jsonify({'error': f'{role_name} role required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Login required'}), 403
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin role required'}), 403
        return f(*args, **kwargs)
    return decorated_function
def teacher_required(fn):
    """确保请求来自教师角色"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'teacher':
            return jsonify({'error': 'Teachers only!'}), 403
        return fn(*args, **kwargs)
    return wrapper