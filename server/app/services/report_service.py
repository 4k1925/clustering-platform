from ..extensions import db
from ..models.report import Report

class ReportService:
    @staticmethod
    def get_user_reports(user_id):
        return Report.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def create_report(user_id, title, content):
        report = Report(user_id=user_id, title=title, content=content)
        db.session.add(report)
        db.session.commit()
        return report
    
    @staticmethod
    def update_report(report_id, user_id, title, content):
        report = Report.query.filter_by(report_id=report_id, user_id=user_id).first()
        if report:
            report.title = title
            report.content = content
            db.session.commit()
        return report
    
    @staticmethod
    def submit_report(report_id, user_id):
        report = Report.query.filter_by(report_id=report_id, user_id=user_id).first()
        if report:
            report.status = 'submitted'
            db.session.commit()
        return report