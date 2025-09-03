from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.clustering_service import (
    simulate_kmeans, 
    simulate_dbscan, 
    simulate_gmm,  # 删除层次聚类，增加GMM
    generate_data_points,
    get_supported_data_types,
    get_supported_centroid_methods
)

clustering_bp = Blueprint('clustering', __name__)

@clustering_bp.route('/data-types', methods=['GET'])
@jwt_required()
def get_data_types():
    """获取支持的数据类型"""
    try:
        data_types = get_supported_data_types()
        return jsonify(data_types)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clustering_bp.route('/centroid-methods', methods=['GET'])
@jwt_required()
def get_centroid_methods():
    """获取质心初始化方法"""
    try:
        methods = get_supported_centroid_methods()
        return jsonify(methods)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clustering_bp.route('/simulate/<algorithm>', methods=['POST'])
@jwt_required()
def simulate_algorithm(algorithm):
    """模拟聚类算法"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # 验证参数
        if not data or 'point_count' not in data:
            return jsonify({'error': '缺少必要参数'}), 400
        
        point_count = data.get('point_count', 100)
        data_type = data.get('data_type', 'uniform')
        
        # 生成数据点
        points = generate_data_points(point_count, data_type)
        
        # 根据算法类型调用不同的模拟函数
        if algorithm == 'kmeans':
            k_value = data.get('k_value', 3)
            centroid_method = data.get('centroid_method', 'random')
            custom_centroids = data.get('custom_centroids')  # 获取自定义质心
            result = simulate_kmeans(points, k_value, centroid_method, custom_centroids)
            
        elif algorithm == 'dbscan':
            epsilon = data.get('epsilon', 0.5)
            min_points = data.get('min_points', 5)
            result = simulate_dbscan(points, epsilon, min_points)
            
        elif algorithm == 'gmm':  # 删除层次聚类，增加GMM
            k_value = data.get('k_value', 3)
            covariance_type = data.get('covariance_type', 'full')
            max_iterations = data.get('max_iterations', 100)
            tolerance = data.get('tolerance', 0.001)
            result = simulate_gmm(points, k_value, covariance_type, max_iterations, tolerance)
            
        else:
            return jsonify({'error': '不支持的算法类型'}), 400
        
        return jsonify({
            'status': 'success',
            'algorithm': algorithm,
            'steps': result['steps'],
            'metrics': result['metrics']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clustering_bp.route('/intro/<algorithm>', methods=['GET'])
def get_algorithm_intro(algorithm):
    """获取算法介绍"""
    intros = {
        'kmeans': {
            'name': 'K-Means聚类',
            'description': '一种基于质心的迭代聚类算法，通过不断更新簇中心点来最小化簇内平方误差',
            'parameters': [
                {'name': 'K值', 'description': '需要聚类的数量'},
                {'name': '质心初始化', 'description': '初始质心的选择方法'}
            ],
            'advantages': [
                '算法简单，易于实现',
                '对于大数据集效率较高',
                '当簇是密集的、球状或团状时，效果较好'
            ],
            'limitations': [
                '需要预先指定K值',
                '对初始质心选择敏感',
                '对噪声和异常点敏感',
                '不适合非凸形状的簇'
            ]
        },
        'dbscan': {
            'name': 'DBSCAN聚类',
            'description': '一种基于密度的聚类算法，能够发现任意形状的簇并识别噪声点',
            'parameters': [
                {'name': 'ε (epsilon)', 'description': '邻域半径，用于定义点的邻域范围'},
                {'name': '最小点数', 'description': '核心点所需的最小邻域点数'}
            ],
            'advantages': [
                '不需要预先指定簇的数量',
                '能够发现任意形状的簇',
                '对噪声数据鲁棒',
                '能够识别噪声点'
            ],
            'limitations': [
                '对参数设置敏感',
                '在高维数据上效果不佳',
                '当簇的密度差异很大时效果不好'
            ]
        },
        'gmm': {  # 删除层次聚类，增加GMM
            'name': '高斯混合模型',
            'description': '基于概率模型的聚类算法，假设数据由多个高斯分布混合生成，通过EM算法进行参数估计',
            'parameters': [
                {'name': '分量数量', 'description': '高斯分布的数量（簇的数量）'},
                {'name': '协方差类型', 'description': '定义高斯分布的协方差矩阵结构'},
                {'name': '最大迭代次数', 'description': 'EM算法的最大迭代次数'},
                {'name': '收敛阈值', 'description': '似然函数变化的收敛阈值'}
            ],
            'advantages': [
                '基于概率模型，提供软聚类',
                '能够处理不同形状和大小的簇',
                '提供每个点的簇隶属概率',
                '有坚实的统计学基础'
            ],
            'limitations': [
                '需要指定高斯分布的数量',
                '对初始值敏感',
                '可能收敛到局部最优',
                '计算复杂度较高'
            ]
        }
    }
    
    if algorithm not in intros:
        return jsonify({'error': '算法不存在'}), 404
    
    return jsonify(intros[algorithm])

@clustering_bp.route('/run', methods=['POST'])
@jwt_required()
def run_cluster_code():
    """运行聚类代码"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        algorithm = data.get('algorithm', '')
        
        # 这里应该实现代码执行的安全沙箱
        # 由于安全原因，这里只返回模拟结果
        
        # 根据算法类型返回不同的示例输出
        if algorithm == 'kmeans':
            output = "K-Means聚类完成！\n簇中心: [[2.1, 3.4], [5.6, 7.8], [9.0, 1.2]]\n轮廓系数: 0.75"
        elif algorithm == 'dbscan':
            output = "DBSCAN聚类完成！\n发现3个簇，15个噪声点\n轮廓系数: 0.68"
        elif algorithm == 'gmm':
            output = "GMM聚类完成！\nBIC: -1250.45, AIC: -1200.32\n收敛: True, 迭代: 25"
        else:
            output = "代码执行功能需要在安全环境中实现"
        
        return jsonify({
            'status': 'success',
            'output': output,
            'result': []
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clustering_bp.route('/videos', methods=['GET'])
def get_video_list():
    """获取教学视频列表"""
    videos = [
        {
            'id': 1,
            'title': 'K-Means算法原理',
            'description': '详细介绍K-Means聚类算法的原理和实现',
            'url': '/videos/kmeans.mp4',
            'duration': '15:30',
            'algorithm': 'kmeans'
        },
        {
            'id': 2,
            'title': 'DBSCAN算法实战',
            'description': '通过实例学习DBSCAN算法的应用',
            'url': '/videos/dbscan.mp4',
            'duration': '12:45',
            'algorithm': 'dbscan'
        },
        {
            'id': 3,  # 增加GMM视频
            'title': '高斯混合模型(GMM)详解',
            'description': '深入讲解GMM算法的数学原理和EM算法',
            'url': '/videos/gmm.mp4',
            'duration': '18:20',
            'algorithm': 'gmm'
        },
        {
            'id': 4,
            'title': 'EM算法推导',
            'description': '详细推导期望最大化(EM)算法的数学原理',
            'url': '/videos/em_algorithm.mp4',
            'duration': '22:15',
            'algorithm': 'gmm'
        }
    ]
    return jsonify(videos)