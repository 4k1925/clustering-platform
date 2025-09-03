# server/app/models/init.py
from app.models.user import User, class_user
from app.models.class_model import Class
from app.models.report import Report
from app.models.score import Score
from app.models.video_history import VideoWatchHistory
from app.models.course_material import CourseMaterial
from app.models.video import Video
from app.models.dict_to import SerializerMixin 
__all__ = [
    'User',
    'Class',
    'class_user',
    'Report',
    'Score',
    'VideoWatchHistory',
    'CourseMaterial',
    'Video',
    'SerializerMixin' # 序列化
]