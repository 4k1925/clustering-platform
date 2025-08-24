# user.
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from datetime import datetime
from app.models.dict_to import SerializerMixin
class_user = db.Table(
    'class_user',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.class_id'), primary_key=True),
    db.Column('join_date', db.DateTime, default=datetime.utcnow)  ,# 记录加入时间
)

class User(db.Model, UserMixin,SerializerMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='student', 
                   comment='用户角色: student/teacher/admin')
    
    # 学生特有字段
    student_id = db.Column(db.String(50), unique=True, nullable=True, comment='学号')
    
    # 关系定义
    classes = db.relationship(
        'Class',
        secondary=class_user,
        back_populates='users',
        lazy='dynamic'
    )
    
    def to_dict(self, exclude=None, include_relationships=False, depth=1):
        """自定义序列化方法（排除敏感信息）"""
        exclude = exclude or []
        exclude.extend(['password_hash'])  # 默认排除密码哈希
        return super().to_dict(exclude, include_relationships, depth)

    # 密码加密处理
    def set_password(self, password):
        """设置密码（自动加密）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    def __repr__(self):
        return f'<User {self.username}>'
