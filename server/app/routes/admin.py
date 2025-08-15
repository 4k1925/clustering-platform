from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    # 实现获取用户列表逻辑
    return jsonify({'message': 'Admin user list endpoint'}), 200

@admin_bp.route('/system-settings')
@login_required
@admin_required
def system_settings():
    # 实现系统设置逻辑
    return jsonify({'message': 'System settings endpoint'}), 200