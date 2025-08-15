from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.report import Report
from app.models.score import Score
from app.services.report_service import ReportService
student_bp = Blueprint('student', __name__)

@student_bp.route('/reports', methods=['GET'])
@login_required
def get_reports():
    reports = ReportService.get_user_reports(current_user.user_id)
    return jsonify([r.to_dict() for r in reports]), 200

@student_bp.route('/reports', methods=['POST'])
@login_required
def create_report():
    data = request.get_json()
    report = ReportService.create_report(
        user_id=current_user.user_id,
        title=data.get('title'),
        content=data.get('content')
    )
    return jsonify(report.to_dict()), 201

@student_bp.route('/reports/<int:report_id>', methods=['PUT'])
@login_required
def update_report(report_id):
    data = request.get_json()
    report = ReportService.update_report(
        report_id=report_id,
        user_id=current_user.user_id,
        title=data.get('title'),
        content=data.get('content')
    )
    return jsonify(report.to_dict()), 200

@student_bp.route('/reports/<int:report_id>/submit', methods=['POST'])
@login_required
def submit_report(report_id):
    report = ReportService.submit_report(report_id, current_user.user_id)
    return jsonify(report.to_dict()), 200

@student_bp.route('/scores', methods=['GET'])
@login_required
def get_scores():
    scores = ReportService.get_user_scores(current_user.user_id)
    return jsonify([s.to_dict() for s in scores]), 200

@student_bp.route('/course-contents', methods=['GET'])
@login_required
def get_course_contents():
    contents = ReportService.get_class_contents(current_user.classes.first().class_id)
    return jsonify([c.to_dict() for c in contents]), 200