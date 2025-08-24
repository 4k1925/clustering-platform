from datetime import datetime
import os
from app.extensions import db
from app.models.dict_to import SerializerMixin

class Report(db.Model, SerializerMixin):
    """实验报告模型
    说明：
    - 学生可以提交多份报告
    - 报告状态机: draft → submitted → reviewed → archived
    - 包含教师评分和反馈功能
    - 支持文件上传
    """
    __tablename__ = 'reports'
    __table_args__ = {'extend_existing': True} 
   
    report_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)  # 改为可选，因为现在主要用文件
    
    # 文件相关字段
    file_name = db.Column(db.String(255), nullable=True, comment='原始文件名')
    file_path = db.Column(db.String(500), nullable=True, comment='服务器存储路径')
    file_size = db.Column(db.Integer, nullable=True, comment='文件大小（字节）')
    file_type = db.Column(db.String(50), nullable=True, comment='文件扩展名')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True, comment='提交时间')
    
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
    
    def get_file_info(self):
        """获取文件信息"""
        return {
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'file_url': f'/api/reports/{self.report_id}/download' if self.file_path else None
        }
    
    def update_file_info(self, file_data):
        """更新文件信息"""
        if file_data:
            self.file_name = file_data.get('file_name')
            self.file_path = file_data.get('file_path')
            self.file_size = file_data.get('file_size')
            self.file_type = file_data.get('file_type')
    
    def submit(self):
        """提交报告"""
        if self.status == 'draft':
            self.status = 'submitted'
            self.submitted_at = datetime.utcnow()
            return True
        return False
    
    def can_edit(self):
        """检查报告是否可编辑"""
        return self.status == 'draft'
    
    def can_delete(self):
        """检查报告是否可删除"""
        return self.status == 'draft'
    
    def __repr__(self):
        return f'<Report {self.title[:20]}>'