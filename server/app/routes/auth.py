from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.decorators import role_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = AuthService.authenticate(data.get('username'), data.get('password'))
    if user:
        login_user(user)
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role
        }), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    success = AuthService.change_password(
        current_user.user_id,  # 这里使用current_user
        data.get('old_password'),
        data.get('new_password')
    )
    if success:
        return jsonify({'message': 'Password updated'}), 200
    return jsonify({'error': 'Password update failed'}), 400