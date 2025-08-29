from app.models.content import CourseContent
import random
import numpy as np
from sklearn.datasets import make_blobs, make_moons
from sklearn.cluster import KMeans, DBSCAN
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt
import io
import base64

class ClusteringService:
    
    def get_algorithm_content(self, algorithm):
        """获取算法介绍内容（简化实现）"""
        # 实际项目中应从数据库获取
        return {
            'title': f'{algorithm} Algorithm',
            'description': f'This is the {algorithm} clustering algorithm',
            'code_template': f'# {algorithm} code template'
        }
    
    def execute_student_code(self, student_id, code, algorithm):
        """执行学生代码（安全沙箱实现）"""
        # 实际项目中应使用安全沙箱执行代码
        # 这里仅返回模拟结果
        return {
            'output': f"Code executed successfully for {algorithm}",
            'success': True
        }
    
    def generate_simulation_data(self, algorithm, params):
        """生成算法模拟数据"""
        point_count = int(params.get('point_count', 100))
        
        if algorithm == 'kmeans':
            k_value = int(params.get('k_value', 3))
            return self._generate_kmeans_data(point_count, k_value)
        elif algorithm == 'dbscan':
            epsilon = float(params.get('epsilon', 0.5))
            min_points = int(params.get('min_points', 3))
            return self._generate_dbscan_data(point_count, epsilon, min_points)
        elif algorithm == 'hierarchical':
            return self._generate_hierarchical_data(point_count)
        else:
            raise ValueError("Unsupported algorithm")
    
    def _generate_kmeans_data(self, point_count, k_value):
        """生成K-Means模拟数据"""
        # 生成随机点
        points = [{'x': random.uniform(0, 500), 'y': random.uniform(0, 500), 'cluster': -1} 
                  for _ in range(point_count)]
        
        # 生成初始质心
        centroids = [{'x': random.uniform(0, 500), 'y': random.uniform(0, 500), 'cluster': i}
                     for i in range(k_value)]
        
        # 模拟K-Means步骤
        steps = [
            {'step': 0, 'description': '随机选择初始质心', 'points': points, 'centroids': centroids}
        ]
        
        # 这里可以添加更多的模拟步骤...
        
        return {'steps': steps}
    
    def _generate_dbscan_data(self, point_count, epsilon, min_points):
        """生成DBSCAN模拟数据"""
        # 生成带簇结构的数据
        X, _ = make_moons(n_samples=point_count, noise=0.05)
        # 缩放并转换为前端需要的格式
        points = [{'x': 250 + x*100, 'y': 250 + y*100, 'cluster': -1} for x, y in X]
        
        steps = [
            {'step': 0, 'description': '初始数据点', 'points': points},
            {'step': 1, 'description': '识别核心点', 'points': points},
            # 更多步骤...
        ]
        
        return {'steps': steps}
    
    def _generate_hierarchical_data(self, point_count):
        """生成层次聚类模拟数据"""
        # 生成随机点
        X, _ = make_blobs(n_samples=min(point_count, 20), centers=3)
        points = [{'x': 250 + x*50, 'y': 250 + y*50, 'cluster': -1} for x, y in X]
        
        steps = [
            {'step': 0, 'description': '初始数据点', 'points': points},
            {'step': 1, 'description': '计算距离矩阵', 'points': points},
            # 更多步骤...
        ]
        
        return {'steps': steps}