from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from ..models.user import User
from ..models.class_model import Class
from ..models.user import class_user  # 关联表模型

class UserService:
    """用户相关服务"""
    
    @staticmethod
    def create_user(username, password, role='student', email=None, student_id=None):
        """创建新用户"""
        if User.query.filter_by(username=username).first():
            raise ValueError('用户名已存在')
            
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        if role == 'student' and student_id:
            user.student_id = student_id
            
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def authenticate(username, password):
        """用户认证"""
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        user = User.query.get(user_id)
        if not user or not check_password_hash(user.password_hash, old_password):
            return False
            
        user.set_password(new_password)
        db.session.commit()
        return True

    def get_user_by_id(user_id):
        """通过ID获取用户"""
        return User.query.get(user_id)

    @staticmethod
    def get_class_students(class_id):
        """获取班级所有学生"""
        return User.query.join(class_user).filter(
            class_user.c.class_id == class_id,
            User.role == 'student'
        ).all()

    @staticmethod
    def add_user_to_class(user_id, class_id):
        """将用户添加到班级"""
        user = User.query.get(user_id)
        class_ = Class.query.get(class_id)
        
        if not user or not class_:
            raise ValueError('用户或班级不存在')
            
        if user not in class_.users:
            class_.users.append(user)
            db.session.commit()
            
        return True

    @staticmethod
    def remove_user_from_class(user_id, class_id):
        """从班级移除用户"""
        user = User.query.get(user_id)
        class_ = Class.query.get(class_id)
        
        if not user or not class_:
            raise ValueError('用户或班级不存在')
            
        if user in class_.users:
            class_.users.remove(user)
            db.session.commit()
            
        return True

    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
            
        allowed_fields = ['email', 'student_id']
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
                
        db.session.commit()
        return user