from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User,class_user
from app.models.class_model import Class
from app.models.report import Report
from app.models.score import Score
from app.models.course_material import CourseMaterial
from app.models.video import Video
# from app.services.user_service import get_user_by_id
from sqlalchemy.exc import SQLAlchemyError  # 添加这行导入
from app.extensions import db
from app.services.teacher_service import (
    get_classes_by_teacher,
    create_class,
    update_class,
    delete_class,
    get_students_in_class,
    import_students_from_excel,
    reset_student_password,
    get_reports_by_class,
    review_report,
    upload_course_material,
)

from app.utils.decorators import teacher_required
from app.utils.helpers import allowed_file
import os
import uuid
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')

@teacher_bp.route('/classes', methods=['GET'])
@jwt_required()
@teacher_required
def get_classes():
    """获取教师的所有班级"""
    teacher_id_str = get_jwt_identity()
    teacher_id = int(teacher_id_str)
    classes = get_classes_by_teacher(teacher_id)
    return jsonify([c.to_dict() for c in classes]), 200

@teacher_bp.route('/classes', methods=['POST'])
@jwt_required()
@teacher_required
def add_class():
    """创建新班级"""
    try:
        teacher_id_str = get_jwt_identity()
        teacher_id = int(teacher_id_str)
        data = request.get_json()
        
        current_app.logger.info(f"Teacher {teacher_id} creating class with data: {data}")
        
        # 数据验证
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
            
        required_fields = ['name', 'course_code']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} 为必填项'}), 400
        
        new_class = create_class(teacher_id, data)
        return jsonify(new_class.to_dict()), 201
        
    except ValueError as e:
        # 处理业务逻辑错误（如课程代码重复）
        current_app.logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
        
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error: {str(e)}")
        # 检查是否是唯一性约束错误
        if "UNIQUE constraint failed" in str(e) and "course_code" in str(e):
            return jsonify({'error': '课程代码已存在，请使用不同的课程代码'}), 400
        return jsonify({'error': '数据库操作失败'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

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
def import_students_route():
    """导入学生列表"""
    upload_path = None
    try:
        current_app.logger.info("=== 开始处理文件导入请求 ===")
        
        # 获取查询参数
        class_id = request.args.get('class_id')
        current_app.logger.info(f"class_id 参数: {class_id}")
        
        if not class_id:
            current_app.logger.error("缺少 class_id 参数")
            return jsonify({'error': 'class_id parameter is required'}), 400
        
        try:
            class_id = int(class_id)
        except ValueError:
            current_app.logger.error(f"class_id 不是有效的整数: {class_id}")
            return jsonify({'error': 'class_id must be a valid integer'}), 400
        
        # 验证班级是否存在
        class_ = Class.query.get(class_id)
        if not class_:
            current_app.logger.error(f"班级不存在: {class_id}")
            return jsonify({'error': f'Class with id {class_id} not found'}), 404
        
        if 'file' not in request.files:
            current_app.logger.error("请求中缺少 'file' 部分")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            current_app.logger.error("文件名为空")
            return jsonify({'error': 'No selected file'}), 400
        
        # 调试信息 - 查看原始文件名
        current_app.logger.info(f"原始文件名: {file.filename}")
        current_app.logger.info(f"安全文件名: {secure_filename(file.filename)}")
        current_app.logger.info(f"文件MIME类型: {file.content_type}")
        
        # 更健壮的文件扩展名提取
        filename = secure_filename(file.filename)
        if '.' in filename:
            file_ext = '.' + filename.rsplit('.', 1)[1].lower()
        else:
            file_ext = ''
        
        current_app.logger.info(f"提取的文件扩展名: '{file_ext}'")
        
        # 支持的文件类型
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        current_app.logger.info(f"允许的扩展名: {allowed_extensions}")
        
        # 如果扩展名检查失败，尝试基于MIME类型判断
        if file_ext not in allowed_extensions:
            # 检查MIME类型
            mime_type = file.content_type.lower()
            current_app.logger.info(f"MIME类型: {mime_type}")
            
            excel_mime_types = [
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel',
                'application/excel',
                'application/x-excel',
                'application/x-msexcel'
            ]
            
            csv_mime_types = [
                'text/csv',
                'text/plain',
                'application/csv',
                'text/comma-separated-values',
                'application/vnd.ms-excel'  # 有时CSV也被识别为excel
            ]
            
            if any(mime in mime_type for mime in excel_mime_types):
                current_app.logger.info("根据MIME类型判断为Excel文件")
                file_ext = '.xlsx'  # 假设为xlsx格式
            elif any(mime in mime_type for mime in csv_mime_types):
                current_app.logger.info("根据MIME类型判断为CSV文件")
                file_ext = '.csv'
            else:
                current_app.logger.error(f"不支持的文件类型: {file_ext}, MIME: {mime_type}")
                return jsonify({'error': 'File type not allowed. Please upload Excel files (.xlsx, .xls) or CSV files (.csv)'}), 400
        
        current_app.logger.info(f"最终确定的文件扩展名: {file_ext}")
        
        # 保存文件
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 确保上传目录存在
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        file.save(upload_path)
        current_app.logger.info(f"文件已保存到: {upload_path}")
        
        result = import_students_from_excel(class_id, upload_path, file_ext)
        
        # 删除临时文件
        if os.path.exists(upload_path):
            os.remove(upload_path)
        
        current_app.logger.info(f"导入结果: {result}")
        
        message = f"导入完成: "
        if result['imported_count'] > 0:
            message += f"新增 {result['imported_count']} 名学生, "
        if result['added_to_class_count'] > 0:
            message += f"添加 {result['added_to_class_count']} 名现有学生到班级, "
        if result['skipped_count'] > 0:
            message += f"跳过 {result['skipped_count']} 名(已在班级中), "
        if result['error_count'] > 0:
            message += f"处理失败 {result['error_count']} 名"
        
        return jsonify({
            'message': message,
            'result': result
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"导入过程中发生错误: {str(e)}", exc_info=True)
        
        # 清理临时文件
        if upload_path and os.path.exists(upload_path):
            try:
                os.remove(upload_path)
            except:
                pass
        
        return jsonify({'error': f'导入失败: {str(e)}'}), 500
    
@teacher_bp.route('/students/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
@teacher_required
def reset_password(user_id):
    """重置学生密码"""
    teacher_id = get_jwt_identity()
    reset_student_password(teacher_id, user_id)
    return jsonify({'message': 'Password reset successfully'}), 200


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

# 后端添加下载接口
@teacher_bp.route('/reports/<int:report_id>/download', methods=['GET'])
@jwt_required()
@teacher_required
def download_report(report_id):
    """下载报告文件"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # 检查教师权限（需要实现）
        # if not has_teacher_access(current_user, report):
        #     return jsonify({'error': '没有权限访问此报告'}), 403
        
        if not report.file_path or not os.path.exists(report.file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(
            report.file_path,
            as_attachment=True,
            download_name=report.file_name or f"report_{report_id}.{report.file_type or 'docx'}"
        )
        
    except Exception as e:
        print(f"下载文件错误: {str(e)}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500
  
@teacher_bp.route('/scores/statistics', methods=['GET'])
@jwt_required()
@teacher_required
def get_score_statistics():
    """获取班级成绩统计"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id parameter is required'}), 400
    
    try:
        # 获取班级所有学生
        students = get_students_in_class(class_id)
        student_ids = [s.user_id for s in students]
        
        # 获取这些学生的所有报告成绩
        reports = Report.query.filter(
            Report.user_id.in_(student_ids),
            Report.status == 'reviewed',
            Report.score.isnot(None)
        ).all()
        
        # 计算统计信息
        scores = [r.score for r in reports if r.score is not None]
        
        if not scores:
            return jsonify({
                'total_students': len(students),
                'submitted_reports': len(reports),
                'statistics': {
                    'score_distribution': {
                        '90-100': 0, '80-89': 0, '70-79': 0,
                        '60-69': 0, '0-59': 0
                    },
                    'average_score': 0,
                    'max_score': 0,
                    'min_score': 0,
                    'pass_rate': 0
                }
            }), 200
        
        # 分数段统计
        score_distribution = {
            '90-100': len([s for s in scores if 90 <= s <= 100]),
            '80-89': len([s for s in scores if 80 <= s < 90]),
            '70-79': len([s for s in scores if 70 <= s < 80]),
            '60-69': len([s for s in scores if 60 <= s < 70]),
            '0-59': len([s for s in scores if s < 60])
        }
        
        # 其他统计信息
        average_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        pass_rate = (len([s for s in scores if s >= 60]) / len(scores)) * 100
        
        return jsonify({
            'total_students': len(students),
            'submitted_reports': len(reports),
            'statistics': {
                'score_distribution': score_distribution,
                'average_score': round(average_score, 2),
                'max_score': max_score,
                'min_score': min_score,
                'pass_rate': round(pass_rate, 2)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取成绩统计失败: {str(e)}")
        return jsonify({'error': f'获取成绩统计失败: {str(e)}'}), 500

@teacher_bp.route('/scores/class/<int:class_id>', methods=['GET'])
@jwt_required()
@teacher_required
def get_class_scores(class_id):
    """获取班级所有学生的成绩"""
    try:
        # 获取班级所有学生
        students = get_students_in_class(class_id)
        
        # 获取每个学生的成绩信息
        student_scores = []
        for student in students:
            # 获取学生的最新报告成绩
            latest_report = Report.query.filter(
                Report.user_id == student.user_id,
                Report.status == 'reviewed'
            ).order_by(Report.submitted_at.desc()).first()
            
            student_scores.append({
                'student_id': student.user_id,
                'student_name': student.username,
                'student_number': student.student_id,
                'score': latest_report.score if latest_report else None,
                'feedback': latest_report.feedback if latest_report else None,
                'report_title': latest_report.title if latest_report else None,
                'submitted_at': latest_report.submitted_at.isoformat() if latest_report and latest_report.submitted_at else None,
                'status': latest_report.status if latest_report else '未提交'
            })
        
        return jsonify(student_scores), 200
        
    except Exception as e:
        current_app.logger.error(f"获取班级成绩失败: {str(e)}")
        return jsonify({'error': f'获取班级成绩失败: {str(e)}'}), 500
    

    # 内容管理路由


# 视频管理路由
@teacher_bp.route('/videos', methods=['GET'])
@jwt_required()
@teacher_required
def get_videos():
    """获取教师上传的视频列表"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id参数是必需的'}), 400
    
    try:
        videos = Video.query.filter_by(course_id=class_id).all()
        return jsonify([video.to_dict() for video in videos]), 200
    except Exception as e:
        current_app.logger.error(f"获取视频列表失败: {str(e)}")
        return jsonify({'error': f'获取视频列表失败: {str(e)}'}), 500

@teacher_bp.route('/videos/upload', methods=['POST'])
@jwt_required()
@teacher_required
def upload_video():
    """上传视频"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "没有文件部分"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "没有选择文件"}), 400
    
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    course_id = request.form.get('course_id')
    user_id = int(get_jwt_identity())
    
    if not course_id:
        return jsonify({"success": False, "message": "缺少课程ID"}), 400
    
    try:
        # 确保上传目录存在
        upload_dir = os.path.join('app', 'uploads', 'videos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # 创建视频记录
        video = Video()
        video.title = title
        video.description = description
        video.file_path = file_path
        video.file_size = file_size
        video.upload_time = datetime.now()
        video.user_id = user_id
        video.course_id = course_id
        
        db.session.add(video)
        db.session.commit()
        
        return jsonify({"success": True, "message": "视频上传成功", "video": video.to_dict()}), 200
    except Exception as e:
        current_app.logger.error(f"视频上传失败: {str(e)}")
        return jsonify({"success": False, "message": f"视频上传失败: {str(e)}"}), 500

@teacher_bp.route('/videos/<int:video_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def update_video(video_id):
    """更新视频信息"""
    data = request.json
    title = data.get('title')
    description = data.get('description')
    
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({"success": False, "message": "视频不存在"}), 404
        
        if title:
            video.title = title
        if description:
            video.description = description
        
        db.session.commit()
        return jsonify({"success": True, "message": "视频信息更新成功", "video": video.to_dict()}), 200
    except Exception as e:
        current_app.logger.error(f"更新视频信息失败: {str(e)}")
        return jsonify({"success": False, "message": f"更新视频信息失败: {str(e)}"}), 500

@teacher_bp.route('/videos/<int:video_id>', methods=['DELETE'])
@jwt_required()
@teacher_required
def delete_video(video_id):
    """删除视频"""
    try:
        video = Video.query.get(video_id)
        if not video:
            return jsonify({"success": False, "message": "视频不存在"}), 404
        
        # 删除文件
        if os.path.exists(video.file_path):
            os.remove(video.file_path)
        
        # 删除数据库记录
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({"success": True, "message": "视频删除成功"}), 200
    except Exception as e:
        current_app.logger.error(f"删除视频失败: {str(e)}")
        return jsonify({"success": False, "message": f"删除视频失败: {str(e)}"}), 500

# 课程资料管理路由
@teacher_bp.route('/materials', methods=['GET'])
@jwt_required()
@teacher_required
def get_materials():
    """获取教师上传的课程资料列表"""
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id参数是必需的'}), 400
    
    try:
        materials = CourseMaterial.query.filter_by(course_id=class_id).all()
        return jsonify([material.to_dict() for material in materials]), 200
    except Exception as e:
        current_app.logger.error(f"获取课程资料列表失败: {str(e)}")
        return jsonify({'error': f'获取课程资料列表失败: {str(e)}'}), 500

@teacher_bp.route('/materials/upload', methods=['POST'])
@jwt_required()
@teacher_required
def upload_material():
    """上传课程资料"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "没有文件部分"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "没有选择文件"}), 400
        
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        course_id = request.form.get('course_id')
        user_id = int(get_jwt_identity())
        
        if not course_id:
            return jsonify({"success": False, "message": "缺少课程ID"}), 400
        
        # 使用服务层函数
        material = upload_course_material(file, title, description, user_id, course_id)
        
        return jsonify({
            "success": True, 
            "message": "资料上传成功", 
            "material": material.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"资料上传失败: {str(e)}")
        return jsonify({"success": False, "message": f"资料上传失败: {str(e)}"}), 500
    
@teacher_bp.route('/materials/<int:material_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def update_material(material_id):
    """更新课程资料信息"""
    data = request.json
    title = data.get('title')
    description = data.get('description')
    
    try:
        material = CourseMaterial.query.get(material_id)
        if not material:
            return jsonify({"success": False, "message": "资料不存在"}), 404
        
        if title:
            material.title = title
        if description:
            material.description = description
        
        db.session.commit()
        return jsonify({"success": True, "message": "资料信息更新成功", "material": material.to_dict()}), 200
    except Exception as e:
        current_app.logger.error(f"更新资料信息失败: {str(e)}")
        return jsonify({"success": False, "message": f"更新资料信息失败: {str(e)}"}), 500

@teacher_bp.route('/materials/<int:material_id>', methods=['DELETE'])
@jwt_required()
@teacher_required
def delete_material(material_id):
    """删除课程资料"""
    try:
        material = CourseMaterial.query.get(material_id)
        if not material:
            return jsonify({"success": False, "message": "资料不存在"}), 404
        
        # 删除文件
        if os.path.exists(material.file_path):
            os.remove(material.file_path)
        
        # 删除数据库记录
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({"success": True, "message": "资料删除成功"}), 200
    except Exception as e:
        current_app.logger.error(f"删除资料失败: {str(e)}")
        return jsonify({"success": False, "message": f"删除资料失败: {str(e)}"}), 500