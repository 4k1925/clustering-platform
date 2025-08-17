from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User,class_user
from app.models.class_model import Class
from app.models.report import Report
from app.models.score import Score
from app.models.content import CourseContent
# from app.services.user_service import get_user_by_id
from app.services.teacher_service import (
    get_classes_by_teacher,
    create_class,
    update_class,
    delete_class,
    get_students_in_class,
    import_students_from_excel,
    reset_student_password,
    get_contents_by_class,
    create_content,
    update_content,
    delete_content,
    get_reports_by_class,
    review_report,
    get_scores_by_class
)
from app.utils.decorators import teacher_required
from app.utils.helpers import allowed_file
import os
import uuid

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/classes', methods=['GET'])
@jwt_required()
@teacher_required
def get_classes():
    """获取教师的所有班级"""
    teacher_id = get_jwt_identity()
    classes = get_classes_by_teacher(teacher_id)
    return jsonify([c.to_dict() for c in classes]), 200

@teacher_bp.route('/classes', methods=['POST'])
@jwt_required()
@teacher_required
def add_class():
    """创建新班级"""
    teacher_id = get_jwt_identity()
    data = request.get_json()
    new_class = create_class(teacher_id, data)
    return jsonify(new_class.to_dict()), 201

@teacher_bp.route('/classes/<int:class_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def modify_class(class_id):
    """更新班级信息"""
    teacher_id = get_jwt_identity()
    data = request.get_json()
    updated_class = update_class(teacher_id, class_id, data)
    return jsonify(updated_class.to_dict()), 200

@teacher_bp.route('/classes/<int:class_id>', methods=['DELETE'])
@jwt_required()
@teacher_required
def remove_class(class_id):
    """删除班级"""
    teacher_id = get_jwt_identity()
    delete_class(teacher_id, class_id)
    return jsonify({'message': 'Class deleted successfully'}), 200

@teacher_bp.route('/students', methods=['GET'])
@jwt_required()
@teacher_required
def get_students():
    """获取班级学生列表"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    students = get_students_in_class(class_id)
    return jsonify([s.to_dict() for s in students]), 200

@teacher_bp.route('/students/import', methods=['POST'])
@jwt_required()
@teacher_required
def import_students():
    """导入学生列表"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename, {'xlsx', 'xls'}):
        filename = secure_filename(file.filename)
        # 生成唯一文件名防止冲突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        try:
            students = import_students_from_excel(class_id, upload_path)
            # 删除临时文件
            os.remove(upload_path)
            return jsonify([s.to_dict() for s in students]), 200
        except Exception as e:
            current_app.logger.error(f"Error importing students: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@teacher_bp.route('/students/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
@teacher_required
def reset_password(user_id):
    """重置学生密码"""
    teacher_id = get_jwt_identity()
    reset_student_password(teacher_id, user_id)
    return jsonify({'message': 'Password reset successfully'}), 200

@teacher_bp.route('/contents', methods=['GET'])
@jwt_required()
@teacher_required
def get_contents():
    """获取班级内容列表"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    contents = get_contents_by_class(class_id)
    return jsonify([c.to_dict() for c in contents]), 200

@teacher_bp.route('/contents', methods=['POST'])
@jwt_required()
@teacher_required
def add_content():
    """创建新内容"""
    teacher_id = get_jwt_identity()
    data = request.get_json()
    new_content = create_content(teacher_id, data)
    return jsonify(new_content.to_dict()), 201

@teacher_bp.route('/contents/<int:content_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def modify_content(content_id):
    """更新内容"""
    teacher_id = get_jwt_identity()
    data = request.get_json()
    updated_content = update_content(teacher_id, content_id, data)
    return jsonify(updated_content.to_dict()), 200

@teacher_bp.route('/contents/<int:content_id>', methods=['DELETE'])
@jwt_required()
@teacher_required
def remove_content(content_id):
    """删除内容"""
    teacher_id = get_jwt_identity()
    delete_content(teacher_id, content_id)
    return jsonify({'message': 'Content deleted successfully'}), 200

@teacher_bp.route('/reports', methods=['GET'])
@jwt_required()
@teacher_required
def get_reports():
    """获取班级报告列表"""
    class_id = request.args.get('class_id')
    status = request.args.get('status', 'submitted')
    
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    reports = get_reports_by_class(class_id, status)
    return jsonify([r.to_dict() for r in reports]), 200

@teacher_bp.route('/reports/<int:report_id>/review', methods=['POST'])
@jwt_required()
@teacher_required
def submit_review(report_id):
    """批阅报告"""
    teacher_id = get_jwt_identity()
    data = request.get_json()
    reviewed_report = review_report(teacher_id, report_id, data)
    return jsonify(reviewed_report.to_dict()), 200

@teacher_bp.route('/scores', methods=['GET'])
@jwt_required()
@teacher_required
def get_scores():
    """获取班级成绩列表"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    scores = get_scores_by_class(class_id)
    return jsonify([s.to_dict() for s in scores]), 200