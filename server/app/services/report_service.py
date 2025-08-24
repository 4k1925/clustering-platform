from app.models.report import Report, db
from app.models.score import Score
from app.utils.exceptions import NotFoundException, UnauthorizedException
import os
import uuid

class ReportService:
    
    def get_student_reports(self, student_id):
        """获取学生的所有实验报告"""
        return Report.query.filter_by(user_id=student_id).order_by(
            Report.created_at.desc()
        ).all()
    
    def create_report(self, student_id, title, file_data):
        """创建新报告（支持文件上传）"""
        new_report = Report(
            title=title,
            content=f"文件报告: {file_data['file_name']}",
            user_id=student_id,
            status='draft',
            file_name=file_data['file_name'],
            file_path=file_data['file_path'],
            file_size=file_data['file_size'],
            file_type=file_data['file_type']
        )
        db.session.add(new_report)
        db.session.commit()
        return new_report
    
    def update_report(self, report_id, student_id, title=None, file_data=None):
        """更新报告（支持文件更新）"""
        report = Report.query.filter_by(
            report_id=report_id,
            user_id=student_id,
            status='draft'  # 只能更新草稿
        ).first()
        
        if not report:
            raise NotFoundException("Report not found or not editable")
        
        if title:
            report.title = title
        
        if file_data:
            # 删除旧文件
            if report.file_path and os.path.exists(report.file_path):
                os.remove(report.file_path)
            
            # 更新文件信息
            report.file_name = file_data['file_name']
            report.file_path = file_data['file_path']
            report.file_size = file_data['file_size']
            report.file_type = file_data['file_type']
            report.content = f"文件报告: {file_data['file_name']}"
        
        db.session.commit()
        return report
    
    def submit_report(self, report_id, student_id):
        """提交报告"""
        report = Report.query.filter_by(
            report_id=report_id,
            user_id=student_id,
            status='draft'  # 只能提交草稿
        ).first()
        
        if not report:
            raise NotFoundException("Report not found or already submitted")
        
        report.status = 'submitted'
        db.session.commit()
        return report
    
    def delete_report(self, report_id, student_id):
        """删除报告"""
        report = Report.query.filter_by(
            report_id=report_id,
            user_id=student_id,
            status='draft'  # 只能删除草稿
        ).first()
        
        if not report:
            raise NotFoundException("Report not found or not deletable")
        
        # 删除文件
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)
        
        db.session.delete(report)
        db.session.commit()
        return report
    
    def get_student_scores(self, student_id):
        """获取学生成绩"""
        return Report.query.filter(
            Report.user_id == student_id,
            Report.status == 'reviewed'
        ).order_by(Report.submitted_at.desc()).all()