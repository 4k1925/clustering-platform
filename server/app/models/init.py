# server/app/models/init.py
from .user import User, class_user
from .class_model import Class
from .report import Report
from .score import Score
from .content import CourseContent# 确保 class_user 被导入
__all__ = [
    'User',
    'Class',
    'class_user',
    'Report',
    'Score',
    'CourseContent'
]