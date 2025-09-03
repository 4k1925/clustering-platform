# server/app/models/content.py
from datetime import datetime
from app.extensions import db
from app.models.dict_to import SerializerMixin
import json

class CourseContent(db.Model, SerializerMixin):
    __tablename__ = 'course_contents'
    
    content_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # video, article, file, code
    body = db.Column(db.Text)  # 用于文章内容
    video_url = db.Column(db.String(500))  # 视频链接
    file_path = db.Column(db.String(500))  # 文件存储路径（新增）
    file_name = db.Column(db.String(255))  # 原始文件名（新增）
    file_size = db.Column(db.Integer)  # 文件大小（字节）（新增）
    tags = db.Column(db.Text, default='[]')  # 标签JSON
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # 关系
    class_obj = db.relationship('Class', backref='contents')
    author = db.relationship('User', backref='contents')

    def __repr__(self):
        return f'<CourseContent {self.title}>'