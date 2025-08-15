from werkzeug.security import generate_password_hash, check_password_hash
from ..models.user import User
from ..extensions import db
from ..utils.exceptions import AuthError
import re

class AuthService:
    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password):
        """验证密码强度"""
        if len(password) < 8:
            return False
        return True

    @staticmethod
    def register_user(username, password, email=None, role='student', student_id=None):
        """注册新用户"""
        if User.query.filter_by(username=username).first():
            raise AuthError('用户名已存在')
        
        if email and User.query.filter_by(email=email).first():
            raise AuthError('邮箱已被注册')
        
        if not AuthService.validate_password(password):
            raise AuthError('密码必须至少8位')
        
        user = User(
            username=username,
            email=email,
            role=role,
            student_id=student_id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login_user(username, password):
        """用户登录"""
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise AuthError('用户名或密码错误')
        return user

    @staticmethod
    def reset_password(user_id, old_password, new_password):
        """重置密码"""
        user = User.query.get(user_id)
        if not user or not user.check_password(old_password):
            raise AuthError('原密码错误')
        
        if not AuthService.validate_password(new_password):
            raise AuthError('新密码必须至少8位')
        
        user.set_password(new_password)
        db.session.commit()
        return True

    @staticmethod
    def get_user_by_email(email):
        """通过邮箱获取用户"""
        return User.query.filter_by(email=email).first()