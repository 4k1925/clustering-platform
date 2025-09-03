from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.extensions import db
from app.models.dict_to import SerializerMixin

class CourseMaterial(db.Model, SerializerMixin):
    """课程资料模型"""
    __tablename__ = 'course_materials'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    file_type = Column(String(50), nullable=False)  # 文件类型
    upload_time = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    course_id = Column(Integer, ForeignKey('classes.class_id'))
    
    # 关系
    user = relationship("User", backref="course_materials")
    course = relationship("Class", backref="course_materials")
    
    def to_dict(self, exclude=None, include_relationships=False, depth=1, **kwargs):
        """扩展序列化方法"""
        exclude = exclude or []
        exclude.extend(['password_hash']) if hasattr(self, 'password_hash') else None
        
        # 先获取基础字段
        data = super().to_dict(exclude=exclude, include_relationships=include_relationships, depth=depth, **kwargs)
        
        # 手动处理特殊字段
        if 'upload_time' in data:
            data['upload_time'] = self.upload_time.strftime('%Y-%m-%d %H:%M:%S')
            
        # 添加关联信息
        if include_relationships and depth > 0:
            data.update({
                'user_name': self.user.username if self.user else None,
                'course_name': self.course.name if self.course else None
            })
            
        return data