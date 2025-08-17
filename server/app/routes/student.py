from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime
import random
from ..extensions import db
from ..models.report import Report
from ..models.content import CourseContent
import traceback

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

@student_bp.route('/videos', methods=['GET'])
@jwt_required()
def get_videos():
    """获取教学视频列表"""
    try:
        videos = CourseContent.query.filter_by(
            content_type='video',
            is_published=True
        ).all()
        
        return jsonify([{
            'id': v.content_id,
            'title': v.title,
            'url': v.video_url,
            'created_at': v.created_at.isoformat()
        } for v in videos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/code/execute', methods=['POST'])
@jwt_required()
def execute_code():
    """执行聚类算法代码"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        # 实际项目应使用安全沙箱执行代码
        # 这里仅返回模拟结果
        return jsonify({
            'output': f"执行成功\n{code[:100]}...",
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """获取实验报告列表"""
    try:
        reports = Report.query.filter_by(
            user_id=current_user.user_id
        ).order_by(Report.created_at.desc()).all()
        
        return jsonify([{
            'id': r.report_id,
            'title': r.title,
            'status': r.status,
            'created_at': r.created_at.isoformat(),
            'score': r.score
        } for r in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    """创建实验报告"""
    try:
        data = request.get_json()
        report = Report(
            title=data['title'],
            content=data['content'],
            user_id=current_user.user_id,
            status='draft'
        )
        db.session.add(report)
        db.session.commit()
        return jsonify({'id': report.report_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """更新实验报告"""
    try:
        report = Report.query.filter_by(
            report_id=report_id,
            user_id=current_user.user_id,
            status='draft'
        ).first_or_404()
        
        data = request.get_json()
        report.title = data.get('title', report.title)
        report.content = data.get('content', report.content)
        db.session.commit()
        return jsonify({'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/reports/<int:report_id>/submit', methods=['POST'])
@jwt_required()
def submit_report(report_id):
    """提交实验报告"""
    try:
        report = Report.query.filter_by(
            report_id=report_id,
            user_id=current_user.user_id,
            status='draft'
        ).first_or_404()
        
        report.status = 'submitted'
        report.submitted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': '提交成功'})
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