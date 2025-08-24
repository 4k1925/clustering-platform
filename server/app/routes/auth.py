# server/app/routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models.user import User
from ..extensions import db
from ..utils.decorators import validate_json
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
@validate_json(['username', 'password'])  # 简化为字段列表验证
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # 手动验证字段
    if len(username) < 1:
        return jsonify({'error': '用户名不能为空'}), 400
    if len(password) < 1:
        return jsonify({'error': '密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    access_token = create_access_token(
        identity=str(user.user_id),
        expires_delta=timedelta(days=7),
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'student_id': user.student_id if user.role == 'student' else None
        },
        'token': access_token
    })

@auth_bp.route('/register', methods=['POST'])
@validate_json(['username', 'password', 'email', 'role'])  # 简化为字段列表验证
def register():
    data = request.get_json()
    
    # 手动添加详细验证
    if len(data['username']) < 3:
        return jsonify({'error': '用户名至少需要3个字符'}), 400
    if len(data['password']) < 6:
        return jsonify({'error': '密码至少需要6个字符'}), 400
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        return jsonify({'error': '邮箱格式不正确'}), 400
    if data['role'] not in ['student', 'teacher']:
        return jsonify({'error': '角色必须是student或teacher'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已注册'}), 400
    
    # 如果是学生，检查学号是否已存在
    if data['role'] == 'student' and 'student_id' in data:
        if User.query.filter_by(student_id=data['student_id']).first():
            return jsonify({'error': '学号已注册'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    if data['role'] == 'student' and 'student_id' in data:
        user.student_id = data['student_id']
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role
        }
    }), 201

@auth_bp.route('/forgot-password', methods=['POST'])
@validate_json(['email'])  # 简化为字段列表验证
def forgot_password():
    data = request.get_json()
    email = data['email']
    
    # 手动验证邮箱格式
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': '该邮箱未注册'}), 404
    
    reset_token = create_access_token(
        identity=user.user_id,
        expires_delta=timedelta(hours=1),
        additional_claims={'purpose': 'password_reset'}
    )
    
    return jsonify({
        'message': '密码重置链接已发送到您的邮箱',
        'reset_token': reset_token
    })

@auth_bp.route('/reset-password', methods=['POST'])
@validate_json(['token', 'new_password'])  # 简化为字段列表验证
def reset_password():
    data = request.get_json()
    token = data['token']
    new_password = data['new_password']
    
    # 手动验证密码长度
    if len(new_password) < 6:
        return jsonify({'error': '密码至少需要6个字符'}), 400
    
    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        
        if decoded.get('purpose') != 'password_reset':
            return jsonify({'error': '无效的token'}), 400
            
        user = User.query.get(decoded['sub'])
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': '密码重置成功'})
    
    except Exception as e:
        return jsonify({'error': '密码重置失败: ' + str(e)}), 400