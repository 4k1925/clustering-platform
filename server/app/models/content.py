# content.py
from datetime import datetime
from app.extensions import db

class CourseContent(db.Model):
    """课程内容模型（教师发布的课程资料）"""
    __tablename__ = 'course_contents'
    
    content_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(50), nullable=False, 
                          comment='内容类型: video/article/code_example')
    body = db.Column(db.Text, nullable=True)  # 富文本内容
    video_url = db.Column(db.String(500), nullable=True)
    attachments = db.Column(db.JSON, nullable=True)  # 存储附件信息
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # 外键关联
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=True)
    
    # 关系定义
    author = db.relationship('User', backref=db.backref('contents', lazy=True))
    class_ = db.relationship('Class', backref=db.backref('contents', lazy=True))
    
    def __repr__(self):
        return f'<CourseContent {self.title}>'