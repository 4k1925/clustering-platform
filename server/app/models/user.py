from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from datetime import datetime

class_user = db.Table(
    'class_user',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.class_id'), primary_key=True),
    db.Column('join_date', db.DateTime, default=datetime.utcnow)  ,# 记录加入时间
)

class User(db.Model, UserMixin):
    """用户数据模型
    说明：
    - 使用UserMixin提供Flask-Login需要的基本方法
    - 密码使用Werkzeug安全哈希存储
    - 通过role字段实现角色权限控制
    """
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