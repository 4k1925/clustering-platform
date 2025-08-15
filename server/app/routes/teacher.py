from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.report import Report
from app.models.score import Score
from app.models.class_model import Class
from app.services.report_service import ReportService
from app.services.user_service import UserService

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/classes', methods=['GET'])
@login_required
def get_classes():
    classes = current_user.classes.all()
    return jsonify([c.to_dict() for c in classes]), 200

@teacher_bp.route('/students', methods=['GET'])
@login_required
def get_students():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    students = UserService.get_class_students(class_id)
    return jsonify([s.to_dict() for s in students]), 200

@teacher_bp.route('/reports', methods=['GET'])
@login_required
def get_class_reports():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    reports = ReportService.get_class_reports(class_id)
    return jsonify([r.to_dict() for r in reports]), 200

@teacher_bp.route('/reports/<int:report_id>/review', methods=['POST'])
@login_required
def review_report(report_id):
    data = request.get_json()
    report = ReportService.review_report(
        report_id=report_id,
        teacher_id=current_user.user_id,
        score=data.get('score'),
        feedback=data.get('feedback')
    )
    return jsonify(report.to_dict()), 200

@teacher_bp.route('/contents', methods=['POST'])
@login_required
def create_content():
    data = request.get_json()
    content = ReportService.create_content(
        author_id=current_user.user_id,
        class_id=data.get('class_id'),
        title=data.get('title'),
        content_type=data.get('content_type'),
        body=data.get('body'),
        video_url=data.get('video_url')
    )
    return jsonify(content.to_dict()), 201