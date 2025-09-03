from datetime import datetime
from app.extensions import db
from app.models.dict_to import SerializerMixin

class VideoWatchHistory(db.Model, SerializerMixin):
    __tablename__ = 'video_watch_history'  # 确保表名正确
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('course_contents.content_id'), nullable=False)  # 正确引用course_contents表
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)
    watch_duration = db.Column(db.Integer, default=0, comment='观看时长(秒)')
    
    # 关系
    user = db.relationship('User', backref='video_watch_history')
    video = db.relationship('CourseContent', backref='watch_history')  # 改为 CourseContent

    def __repr__(self):
        return f'<VideoWatchHistory user:{self.user_id} video:{self.video_id}>'