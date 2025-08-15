# class_model.py
from datetime import datetime
from ..extensions import db

class Class(db.Model):
    """班级数据模型
    说明：
    - 一个班级包含多个用户(学生/教师)
    - 通过class_user关联表实现多对多关系
    - 教师可以管理多个班级
    """
    __tablename__ = 'classes'
    
    class_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='班级名称')
    course_code = db.Column(db.String(50), unique=True)  # 新增课程代码
    academic_year = db.Column(db.String(20))  # 如 "2023-2024"
    description = db.Column(db.Text, comment='班级描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系定义
    users = db.relationship(
        'User', 
        secondary='class_user',
        back_populates='classes',
        lazy='dynamic'  # 延迟加载
    )
    
    def __repr__(self):
        return f'<Class {self.name}>'