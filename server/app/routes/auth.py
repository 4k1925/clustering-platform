from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..services.auth_service import AuthService
from ..utils.exceptions import AuthError
from ..models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        user = AuthService.register_user(
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email'),
            role=data.get('role', 'student'),
            student_id=data.get('student_id')
        )
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': user.user_id,
                'username': user.username,
                'role': user.role
            }
        }), 201
    except AuthError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        user = AuthService.login_user(
            username=data.get('username'),
            password=data.get('password')
        )
        access_token = create_access_token(identity={
            'id': user.user_id,
            'username': user.username,
            'role': user.role
        })
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.user_id,
                'username': user.username,
                'role': user.role
            }
        })
    except AuthError as e:
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/reset-password', methods=['POST'])
@jwt_required()
def reset_password():
    current_user = get_jwt_identity()
    data = request.get_json()
    try:
        AuthService.reset_password(
            user_id=current_user['id'],
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        return jsonify({'message': '密码修改成功'})
    except AuthError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    # 这里简化处理，实际应该发送重置链接到邮箱
    email = request.json.get('email')
    user = AuthService.get_user_by_email(email)
    if not user:
        return jsonify({'error': '邮箱未注册'}), 404
    # 实际应用中这里应该生成token并发送重置邮件
    return jsonify({'message': '重置链接已发送到您的邮箱(模拟)'})