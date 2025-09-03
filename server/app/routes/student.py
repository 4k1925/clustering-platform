import os
import uuid
from flask import Blueprint, current_app, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user
from datetime import datetime
import random
from ..extensions import db
from ..models.report import Report
from ..models.class_model import Class
from ..models.user import User,class_user
from ..models.video import Video
from ..models.course_material import CourseMaterial
import traceback
from app.services.code_execution_service import SecurityError, code_executor
       
# 创建学生蓝图
student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/algorithms/<algorithm>', methods=['GET'])
@jwt_required()
def get_algorithm_content(algorithm):
    """获取聚类算法介绍内容"""
    try:
        algorithms = {
            'kmeans': {
                'title': 'K-Means聚类',
                'description': '基于距离的划分聚类方法',
                'steps': ['1. 随机选择K个中心点', '2. 计算距离分配点', '3. 重新计算中心点', '4. 迭代直到收敛'],
                'code_template': 'from sklearn.cluster import KMeans\n# 示例代码...'
            },
            'dbscan': {
                'title': 'DBSCAN聚类',
                'description': '基于密度的聚类方法',
                'steps': ['1. 寻找核心点', '2. 扩展聚类', '3. 标记噪声点'],
                'code_template': 'from sklearn.cluster import DBSCAN\n# 示例代码...'
            },
            'hierarchical': {
                'title': '层次聚类',
                'description': '构建树形结构的聚类方法',
                'steps': ['1. 计算距离矩阵', '2. 合并最近簇', '3. 更新距离矩阵', '4. 重复直到完成'],
                'code_template': 'from scipy.cluster.hierarchy import linkage\n# 示例代码...'
            }
        }
        
        if algorithm not in algorithms:
            return jsonify({'error': 'Algorithm not found'}), 404
            
        return jsonify(algorithms[algorithm])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 视频访问路由
@student_bp.route('/videos', methods=['GET'])
@jwt_required()
def get_videos():
    """获取学生可访问的视频列表"""
    try:
        # 获取学生所在的班级ID
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        class_ids = [cls.class_id for cls in student_classes]
        
        if not class_ids:
            return jsonify([]), 200
            
        # 查询这些班级中的视频
        videos = Video.query.filter(
            Video.course_id.in_(class_ids)
        ).order_by(Video.upload_time.desc()).all()
        
        return jsonify([video.to_dict() for video in videos]), 200
    except Exception as e:
        print(f"获取视频列表失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/videos/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """获取单个视频详情"""
    try:
        video = Video.query.get_or_404(video_id)
        
        # 检查权限：学生必须在该视频的班级中
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        class_ids = [cls.class_id for cls in student_classes]
        if video.course_id not in class_ids:
            return jsonify({'error': '没有权限访问此视频'}), 403
        
        return jsonify(video.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/videos/<int:video_id>/stream', methods=['GET'])
@jwt_required()
def stream_video(video_id):
    """流式传输视频"""
    try:
        video = Video.query.get_or_404(video_id)
        
        # 检查权限：学生必须在该视频的班级中
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        class_ids = [cls.class_id for cls in student_classes]
        if video.course_id not in class_ids:
            return jsonify({'error': '没有权限访问此视频'}), 403
        
        if not video.file_path or not os.path.exists(video.file_path):
            return jsonify({'error': '视频文件不存在'}), 404
        
        return send_file(video.file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 课程资料访问路由
@student_bp.route('/materials', methods=['GET'])
@jwt_required()
def get_materials():
    """获取学生可访问的课程资料列表"""
    try:
        # 获取学生所在的班级ID
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        class_ids = [cls.class_id for cls in student_classes]
        
        if not class_ids:
            return jsonify([]), 200
            
        # 查询这些班级中的课程资料
        materials = CourseMaterial.query.filter(
            CourseMaterial.course_id.in_(class_ids)
        ).order_by(CourseMaterial.upload_time.desc()).all()
        
        return jsonify([material.to_dict() for material in materials]), 200
    except Exception as e:
        print(f"获取课程资料列表失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/materials/<int:material_id>', methods=['GET'])
@jwt_required()
def get_material(material_id):
    """获取单个课程资料详情"""
    try:
        material = CourseMaterial.query.get_or_404(material_id)
        
        # 检查权限：学生必须在该资料的班级中
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        class_ids = [cls.class_id for cls in student_classes]
        if material.course_id not in class_ids:
            return jsonify({'error': '没有权限访问此资料'}), 403
        
        return jsonify(material.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/materials/<int:material_id>/download', methods=['GET'])
@jwt_required()
def download_material(material_id):
    """下载课程资料"""
    try:
        material = CourseMaterial.query.get_or_404(material_id)
        
        # 检查权限：学生必须在该资料的班级中
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        class_ids = [cls.class_id for cls in student_classes]
        if material.course_id not in class_ids:
            return jsonify({'error': '没有权限访问此资料'}), 403
        
        if not material.file_path or not os.path.exists(material.file_path):
            return jsonify({'error': '资料文件不存在'}), 404
        
        return send_file(
            material.file_path,
            as_attachment=True,
            download_name=material.title + os.path.splitext(material.file_path)[1]
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/code/execute', methods=['POST'])
@jwt_required()
def execute_code():
    """执行聚类算法代码"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({'error': '代码不能为空'}), 400
        result = code_executor.execute_code(code)
        
        if result['success']:
            return jsonify({
                'output': result['output'],
                'error': result['error'],
                'images': result['images'],
                'status': 'success'
            })
        else:
            return jsonify({
                'output': result['output'],
                'error': result['error'],
                'images': [],
                'status': 'error'
            }), 400
            
    except SecurityError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'执行失败: {str(e)}'}), 500

# 允许的文件类型
ALLOWED_EXTENSIONS = {'doc', 'docx', 'pdf', 'wps', 'txt', 'md', 'zip', 'rar'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@student_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    try:
        reports = Report.query.filter_by(user_id=current_user.user_id).all()
        print(f"查询到的报告数量: {len(reports)}")
        
        if not reports:
            return jsonify([]), 200
            
        # 直接使用模型的 to_dict 方法
        reports_data = []
        for report in reports:
            data = report.to_dict(exclude=['file_path'])
            
            # 手动添加文件下载URL
            if report.file_path and os.path.exists(report.file_path):
                data['file_url'] = f'/api/student/reports/{report.report_id}/download'
            else:
                data['file_url'] = None
                
            reports_data.append(data)
        
        print(f"返回数据: {reports_data}")
        return jsonify(reports_data), 200
        
    except Exception as e:
        print(f"获取报告错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '请选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '请选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': '文件大小不能超过50MB'}), 400
        
        # 获取标题
        title = request.form.get('title', '').strip()
        if not title:
            title = os.path.splitext(file.filename or '')[0]
        
        # 创建上传目录
        upload_dir = os.path.join('uploads', 'reports', str(current_user.user_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename or '')[1].lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 创建报告记录
        report = Report(
            user_id=current_user.user_id,
            title=title,
            content=f"文件报告: {file.filename}",
            file_name=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext[1:],
            status='draft'
        )
        
        db.session.add(report)
        db.session.commit()
        report_data = report.to_dict(exclude=['file_path'])
        if report.file_path and os.path.exists(report.file_path):
            report_data['file_url'] = f'/api/student/reports/{report.report_id}/download'
        else:
            report_data['file_url'] = None
        
        print(f"创建报告成功: {report_data}")
        return jsonify(report_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"创建报告错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    try:
        report = Report.query.filter_by(
            report_id=report_id, 
            user_id=current_user.user_id
        ).first()
        
        if not report:
            return jsonify({'error': '报告不存在'}), 404
        
        if not report.can_edit():
            return jsonify({'error': '已提交的报告不能修改'}), 400
        
        # 更新标题
        if 'title' in request.form:
            title = request.form.get('title')
            if title:
                report.title = title.strip()
        
        # 更新文件（如果有）
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                if not allowed_file(file.filename):
                    return jsonify({'error': '不支持的文件类型'}), 400
                
                # 检查文件大小
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    return jsonify({'error': '文件大小不能超过50MB'}), 400
                
                # 删除旧文件
                if report.file_path and os.path.exists(report.file_path):
                    os.remove(report.file_path)
                
                # 保存新文件
                file_ext = os.path.splitext(file.filename or '')[1].lower()
                unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                file_path = os.path.join('uploads', 'reports', str(current_user.user_id), unique_filename)
                
                file.save(file_path)
                
                # 更新文件信息
                report.file_name = file.filename
                report.file_path = file_path
                report.file_size = file_size
                report.file_type = file_ext[1:]
                report.content = f"文件报告: {file.filename}"
        
        report.updated_at = datetime.utcnow()
        db.session.commit()
        report_data = report.to_dict(exclude=['file_path'])
        if report.file_path and os.path.exists(report.file_path):
            report_data['file_url'] = f'/api/student/reports/{report.report_id}/download'
        else:
            report_data['file_url'] = None
        
        return jsonify(report_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports/<int:report_id>/submit', methods=['POST'])
@jwt_required()
def submit_report(report_id):
    try:
        report = Report.query.filter_by(
            report_id=report_id, 
            user_id=current_user.user_id
        ).first()
        
        if not report:
            return jsonify({'error': '报告不存在'}), 404
        
        if report.submit():
            db.session.commit()
            return jsonify({'message': '报告提交成功'}), 200
        else:
            return jsonify({'error': '报告状态不允许提交'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports/<int:report_id>/download', methods=['GET'])
@jwt_required()
def download_report(report_id):
    try:
        report = Report.query.filter_by(report_id=report_id).first()
        
        if not report:
            return jsonify({'error': '报告不存在'}), 404
        
        # 检查权限：要么是报告作者，要么是教师
        if (report.user_id != current_user.user_id and 
            current_user.role not in ['teacher', 'admin']):
            return jsonify({'error': '没有权限'}), 403
        
        if not report.file_path or not os.path.exists(report.file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(
            report.file_path,
            as_attachment=True,
            download_name=report.file_name or f"report_{report_id}{os.path.splitext(report.file_path)[1]}"
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    try:
        report = Report.query.filter_by(
            report_id=report_id, 
            user_id=current_user.user_id
        ).first()
        
        if not report:
            return jsonify({'error': '报告不存在'}), 404
        
        if not report.can_delete():
            return jsonify({'error': '已提交的报告不能删除'}), 400
        
        # 删除文件
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': '报告删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/scores', methods=['GET'])
@jwt_required()
def get_scores():
    """获取成绩信息"""
    try:
        reports = Report.query.filter(
            Report.user_id == current_user.user_id,
            Report.status == 'reviewed'
        ).all()
        
        return jsonify([{
            'report_id': r.report_id,
            'title': r.title,
            'score': r.score,
            'feedback': r.feedback
        } for r in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/classes', methods=['GET'])
@jwt_required()
def get_student_classes():
    """获取学生所在班级"""
    try:
        # 获取学生所在的班级
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        return jsonify([{
            'class_id': cls.class_id,
            'name': cls.name,
            'course_code': cls.course_code,
            'academic_year': cls.academic_year,
            'description': cls.description
        } for cls in student_classes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/contents', methods=['GET'])
@jwt_required()
def get_student_contents():
    """获取学生课程内容"""
    try:
        class_id = request.args.get('class_id')
        if not class_id:
            return jsonify({'error': 'class_id parameter is required'}), 400
        
        # 验证学生是否在该班级
        class_member = db.session.query(class_user).filter(
            class_user.c.class_id == class_id,
            class_user.c.user_id == current_user.user_id
        ).first()
        
        if not class_member:
            return jsonify({'error': 'Access denied'}), 403
        
        # 获取该班级的已发布内容
        contents = CourseContent.query.filter_by(
            class_id=class_id,
            is_published=True
        ).order_by(CourseContent.created_at.desc()).all()
        
        return jsonify([{
            'content_id': c.content_id,
            'title': c.title,
            'content_type': c.content_type,
            'body': c.body,
            'video_url': c.video_url,
            'attachments': c.attachments,
            'is_published': c.is_published,
            'created_at': c.created_at.isoformat(),
            'updated_at': c.updated_at.isoformat() if c.updated_at else None
        } for c in contents])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/simulation/<algorithm>', methods=['GET'])
@jwt_required()
def get_simulation(algorithm):
    """获取算法模拟数据"""
    try:
        params = {
            'point_count': int(request.args.get('point_count', 100)),
            'k_value': int(request.args.get('k_value', 3)),
            'epsilon': float(request.args.get('epsilon', 0.5)),
            'min_points': int(request.args.get('min_points', 3))
        }
        
        # 生成模拟数据
        points = [{
            'x': random.uniform(0, 10),
            'y': random.uniform(0, 10),
            'cluster': i % 3
        } for i in range(params['point_count'])]
        
        return jsonify({
            'algorithm': algorithm,
            'parameters': params,
            'data': points
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


    """下载内容文件"""
    try:
        content = CourseContent.query.get_or_404(content_id)
        
        # 检查权限：学生必须在该内容的班级中
        student_classes = Class.query.join(class_user).filter(
            class_user.c.user_id == current_user.user_id
        ).all()
        
        class_ids = [cls.class_id for cls in student_classes]
        if content.class_id not in class_ids:
            return jsonify({'error': '没有权限访问此内容'}), 403
        
        if not content.file_path or not os.path.exists(content.file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(
            content.file_path,
            as_attachment=True,
            download_name=content.file_name or f"content_{content_id}"
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500