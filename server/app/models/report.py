# report.py
from datetime import datetime
from app.extensions import db
from app.models.dict_to import SerializerMixin
class Report(db.Model, SerializerMixin):
    """实验报告模型
    说明：
    - 学生可以提交多份报告
    - 报告状态机: draft → submitted → reviewed → archived
    - 包含教师评分和反馈功能
    """
    __tablename__ = 'reports'
    __table_args__ = {'extend_existing': True} 
   
    report_id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # 状态管理
    status = db.Column(db.String(20), default='draft', 
                      comment='报告状态: draft/submitted/reviewed/archived')
    
    # 外键关联
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    # 评分相关
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text)
    
    # 关系定义
    author = db.relationship('User', backref=db.backref('reports', lazy=True))
    
    def __repr__(self):
        return f'<Report {self.title[:20]}>'