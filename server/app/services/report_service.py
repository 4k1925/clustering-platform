from app.models.report import Report,  db
from app.models.score import Score
from app.utils.exceptions import NotFoundException, UnauthorizedException

class ReportService:
    
    def get_student_reports(self, student_id):
        """获取学生的所有实验报告"""
        return Report.query.filter_by(user_id=student_id).order_by(
            Report.created_at.desc()
        ).all()
    
    def create_report(self, student_id, title, content):
        """创建新报告"""
        new_report = Report(
            title=title,
            content=content,
            user_id=student_id,
            status='draft'
        )
        db.session.add(new_report)
        db.session.commit()
        return new_report
    
    def update_report(self, report_id, student_id, title=None, content=None):
        """更新报告"""
        report = Report.query.filter_by(
            report_id=report_id,
            user_id=student_id,
            status='draft'  # 只能更新草稿
        ).first()
        
        if not report:
            raise NotFoundException("Report not found or not editable")
        
        if title:
            report.title = title
        if content:
            report.content = content
        
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
        
        db.session.delete(report)
        db.session.commit()
        return report
    
    def get_student_scores(self, student_id):
        """获取学生成绩"""
        return Report.query.filter(
            Report.user_id == student_id,
            Report.status == 'reviewed'
        ).order_by(Report.submitted_at.desc()).all()