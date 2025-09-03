from app.models.content import CourseContent
import random
import numpy as np
from sklearn.datasets import make_blobs, make_moons
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from scipy import linalg
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
        elif algorithm == 'gmm':
            n_components = int(params.get('n_components', 3))
            covariance_type = params.get('covariance_type', 'full')
            return self._generate_gmm_data(point_count, n_components, covariance_type)
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
    
    def _generate_gmm_data(self, point_count, n_components, covariance_type):
        """生成高斯混合聚类模拟数据"""
        # 生成符合高斯分布的数据
        X, true_labels = make_blobs(
            n_samples=point_count, 
            centers=n_components,
            cluster_std=0.8,
            random_state=42
        )
        
        # 缩放并转换为前端需要的格式
        points = [{'x': 250 + x*80, 'y': 250 + y*80, 'cluster': -1, 'probability': [0]*n_components} 
                 for x, y in X]
        
        # 训练GMM模型
        gmm = GaussianMixture(
            n_components=n_components,
            covariance_type=covariance_type,
            random_state=42
        )
        gmm.fit(X)
        
        # 获取预测结果
        labels = gmm.predict(X)
        probabilities = gmm.predict_proba(X)
        
        # 更新点的聚类标签和概率
        for i, point in enumerate(points):
            point['cluster'] = int(labels[i])
            point['probability'] = probabilities[i].tolist()
        
        # 准备高斯分布信息（均值和协方差）
        gaussians = []
        for i in range(n_components):
            mean = gmm.means_[i]
            cov = gmm.covariances_[i]
            gaussians.append({
                'mean': {'x': 250 + mean[0]*80, 'y': 250 + mean[1]*80},
                'covariance': cov.tolist(),
                'weight': float(gmm.weights_[i])
            })
        
        steps = [
            {
                'step': 0, 
                'description': '初始数据点和高斯分布初始化', 
                'points': points,
                'gaussians': gaussians
            },
            {
                'step': 1, 
                'description': 'EM算法执行后 - 期望步骤(E-step)', 
                'points': points,
                'gaussians': gaussians
            },
            {
                'step': 2, 
                'description': 'EM算法执行后 - 最大化步骤(M-step)', 
                'points': points,
                'gaussians': gaussians
            },
            {
                'step': 3, 
                'description': '最终聚类结果', 
                'points': points,
                'gaussians': gaussians
            }
        ]
        
        return {'steps': steps, 'gmm_info': {
            'converged': gmm.converged_,
            'n_iter': gmm.n_iter_,
            'aic': gmm.aic(X),
            'bic': gmm.bic(X)
        }}
    
    def perform_gmm(self, data, n_components=3, covariance_type='full', random_state=42):
        """执行高斯混合聚类"""
        try:
            # 转换数据格式
            X = np.array([[point['x'], point['y']] for point in data])
            
            # 执行GMM聚类
            gmm = GaussianMixture(
                n_components=n_components,
                covariance_type=covariance_type,
                random_state=random_state
            )
            gmm.fit(X)
            
            # 获取结果
            labels = gmm.predict(X)
            probabilities = gmm.predict_proba(X)
            
            # 准备返回结果
            result = {
                'labels': labels.tolist(),
                'probabilities': probabilities.tolist(),
                'converged': gmm.converged_,
                'n_iter': gmm.n_iter_,
                'weights': gmm.weights_.tolist(),
                'means': gmm.means_.tolist(),
                'covariances': [cov.tolist() for cov in gmm.covariances_],
                'aic': gmm.aic(X),
                'bic': gmm.bic(X)
            }
            
            # 生成可视化图像
            plt.figure(figsize=(10, 8))
            plt.scatter(X[:, 0], X[:, 1], c=labels, s=50, cmap='viridis', alpha=0.6)
            
            # 绘制高斯分布的椭圆
            for i in range(n_components):
                if gmm.covariances_[i].shape == (2, 2):
                    v, w = linalg.eigh(gmm.covariances_[i])
                    u = w[0] / linalg.norm(w[0])
                    angle = np.arctan2(u[1], u[0])
                    angle = 180 * angle / np.pi
                    v = 2. * np.sqrt(2.) * np.sqrt(v)
                    ell = plt.matplotlib.patches.Ellipse(
                        gmm.means_[i], v[0], v[1], 180 + angle,
                        color='red', alpha=gmm.weights_[i] * 2
                    )
                    ell.set_clip_box(plt.gca().bbox)
                    ell.set_alpha(0.3)
                    plt.gca().add_artist(ell)
            
            plt.title('Gaussian Mixture Model Clustering')
            plt.xlabel('Feature 1')
            plt.ylabel('Feature 2')
            plt.grid(True, alpha=0.3)
            
            # 保存图像为base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            result['plot'] = f'data:image/png;base64,{image_base64}'
            
            return result
            
        except Exception as e:
            raise Exception(f"GMM clustering failed: {str(e)}")