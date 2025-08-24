# score.py
from datetime import datetime
from app.extensions import db
from app.models.dict_to import SerializerMixin

class Score(db.Model, SerializerMixin):

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