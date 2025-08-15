from datetime import datetime
from ..extensions import db

class Score(db.Model):
    """评分模型（独立出来便于扩展）
    说明：
    - 单独存储评分记录便于历史追溯
    - 一个报告可以有多个评分版本
    """
    __tablename__ = 'scores'
    
    score_id = db.Column(db.Integer, primary_key=True)
    score_value = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键关联
    report_id = db.Column(db.Integer, db.ForeignKey('reports.report_id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    # 关系定义
    report = db.relationship('Report', backref=db.backref('score_records', lazy=True))
    teacher = db.relationship('User', backref=db.backref('given_scores', lazy=True))
    
    def __repr__(self):
        return f'<Score {self.score_value}>'