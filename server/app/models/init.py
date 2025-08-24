# server/app/models/init.py
from app.models.user import User, class_user
from app.models.class_model import Class
from app.models.report import Report
from app.models.score import Score
from app.models.content import CourseContent# 确保 class_user 被导入
from app.models.dict_to import SerializerMixin 
__all__ = [
    'User',
    'Class',
    'class_user',
    'Report',
    'Score',
    'CourseContent',
    'SerializerMixin'
]