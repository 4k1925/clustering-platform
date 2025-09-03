import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture  # 删除层次聚类，增加GMM
from sklearn.datasets import make_blobs, make_moons, make_circles
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import json
def generate_data_points(n_samples, data_type='uniform'):
    """生成不同类型的数据点"""
    if data_type == 'gaussian':
        # 生成高斯分布数据
        points, labels = make_blobs(
            n_samples=n_samples, 
            centers=3, 
            cluster_std=0.8, 
            random_state=42
        )
    elif data_type == 'moons':
        # 生成月牙形数据
        points, labels = make_moons(
            n_samples=n_samples, 
            noise=0.1, 
            random_state=42
        )
    elif data_type == 'circles':
        # 生成环形数据
        points, labels = make_circles(
            n_samples=n_samples, 
            noise=0.05, 
            factor=0.5, 
            random_state=42
        )
    elif data_type == 'smiley':
        # 生成笑脸分布数据
        points, labels = generate_smiley_data(n_samples)
    elif data_type == 'spiral':
        # 生成螺旋分布数据
        points, labels = generate_spiral_data(n_samples)
    elif data_type == 'anisotropic':
        # 生成异方差分布数据
        points, labels = generate_anisotropic_data(n_samples)
    elif data_type == 'noisy':
        # 生成带噪声的数据
        points, labels = generate_noisy_data(n_samples)
    else:
        # 默认均匀分布
        np.random.seed(42)
        points = np.random.rand(n_samples, 2) * 10
        labels = np.zeros(n_samples)
    
    # 转换为前端需要的格式
    formatted_points = []
    for i, point in enumerate(points):
        formatted_points.append({
            'x': float(point[0]),
            'y': float(point[1]),
            'cluster': int(labels[i]) if i < len(labels) else -1,
            'originalCluster': int(labels[i]) if i < len(labels) else -1
        })
    
    return formatted_points


def generate_smiley_data(n_samples):
    """生成笑脸形状的数据 - 最终修正版"""
    np.random.seed(42)
    
    # 精确计算各部分点数
    n_face = n_samples // 2
    n_eye = n_samples // 8
    n_mouth = n_samples - n_face - 2 * n_eye
    
    points = []
    labels = []
    
    # 1. 脸轮廓 (大圆)
    angles = np.random.uniform(0, 2 * np.pi, n_face)
    radii = np.random.uniform(3.5, 4.5, n_face)
    face_x = 5 + radii * np.cos(angles)
    face_y = 5 + radii * np.sin(angles)
    points.extend(np.column_stack([face_x, face_y]))
    labels.extend([0] * n_face)
    
    # 2. 左眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)
    left_eye_x = 3.5 + radii * np.cos(angles)
    left_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([left_eye_x, left_eye_y]))
    labels.extend([1] * n_eye)
    
    # 3. 右眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)
    right_eye_x = 6.5 + radii * np.cos(angles)
    right_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([right_eye_x, right_eye_y]))
    labels.extend([2] * n_eye)
    
    # 4. 嘴巴 (向下弧形) - 关键修正！
    # 使用下半圆的角度范围：π 到 2π (180° 到 360°)
    angles = np.random.uniform(np.pi, 2 * np.pi, n_mouth)
    radii = np.random.uniform(1.5, 2.0, n_mouth)  # 减小半径
    
    mouth_x = 5 + radii * np.cos(angles)
    mouth_y = 4.5 + radii * np.sin(angles)  # 中心点下移
    
    points.extend(np.column_stack([mouth_x, mouth_y]))
    labels.extend([3] * n_mouth)
    
    points = np.array(points)
    labels = np.array(labels)
    
    # 确保坐标在 0-10 范围内
    points = np.clip(points, 0.1, 9.9)
    
    # 打乱顺序
    indices = np.random.permutation(len(points))
    return points[indices], labels[indices]
    """生成笑脸形状的数据 - 修正版"""
    np.random.seed(42)
    
    # 精确计算各部分点数
    n_face = n_samples // 2
    n_eye = n_samples // 8
    n_mouth = n_samples - n_face - 2 * n_eye
    
    points = []
    labels = []
    
    # 1. 脸轮廓 (大圆)
    angles = np.random.uniform(0, 2 * np.pi, n_face)
    radii = np.random.uniform(3.5, 4.5, n_face)
    face_x = 5 + radii * np.cos(angles)
    face_y = 5 + radii * np.sin(angles)
    points.extend(np.column_stack([face_x, face_y]))
    labels.extend([0] * n_face)
    
    # 2. 左眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)
    left_eye_x = 3.5 + radii * np.cos(angles)
    left_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([left_eye_x, left_eye_y]))
    labels.extend([1] * n_eye)
    
    # 3. 右眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)
    right_eye_x = 6.5 + radii * np.cos(angles)
    right_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([right_eye_x, right_eye_y]))
    labels.extend([2] * n_eye)
    
    # 4. 嘴巴 (向下弧形) - 修正部分
    angles = np.random.uniform(np.pi * 0.2, np.pi * 0.8, n_mouth)
    radii = np.random.uniform(2.0, 2.5, n_mouth)
    mouth_x = 5 + radii * np.cos(angles)  # 中心点x坐标修正为5
    mouth_y = 4 + radii * np.sin(angles)  # 中心点y坐标下移
    points.extend(np.column_stack([mouth_x, mouth_y]))
    labels.extend([3] * n_mouth)
    
    points = np.array(points)
    labels = np.array(labels)
    
    # 确保坐标在 0-10 范围内
    points = np.clip(points, 0.1, 9.9)
    
    # 打乱顺序
    indices = np.random.permutation(len(points))
    return points[indices], labels[indices]
    """生成笑脸形状的数据 - 修正版"""
    np.random.seed(42)
    
    # 精确计算各部分点数，避免整数除法误差
    n_face = n_samples // 2
    n_eye = n_samples // 8
    n_mouth = n_samples - n_face - 2 * n_eye  # 剩余点数给嘴巴
    
    points = []
    labels = []
    
    # 1. 脸轮廓 (大圆)
    angles = np.random.uniform(0, 2 * np.pi, n_face)
    radii = np.random.uniform(3.5, 4.5, n_face)  # 调整半径范围
    face_x = 5 + radii * np.cos(angles)
    face_y = 5 + radii * np.sin(angles)
    points.extend(np.column_stack([face_x, face_y]))
    labels.extend([0] * n_face)
    
    # 2. 左眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)  # 调整半径范围
    left_eye_x = 3.5 + radii * np.cos(angles)
    left_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([left_eye_x, left_eye_y]))
    labels.extend([1] * n_eye)
    
    # 3. 右眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)  # 调整半径范围
    right_eye_x = 6.5 + radii * np.cos(angles)
    right_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([right_eye_x, right_eye_y]))
    labels.extend([2] * n_eye)
    
    # 4. 嘴巴 (向下弧形) - 修正这里！
    # 嘴巴应该是向下的弧形，角度从 0.2π 到 0.8π（下半圆）
    angles = np.random.uniform(np.pi * 0.2, np.pi * 0.8, n_mouth)
    radii = np.random.uniform(2.0, 2.5, n_mouth)  # 调整半径范围
    mouth_x = 2 + radii * np.cos(angles)
    mouth_y = 2 + radii * np.sin(angles)  # 保持y坐标计算不变
    points.extend(np.column_stack([mouth_x, mouth_y]))
    labels.extend([3] * n_mouth)
    
    points = np.array(points)
    labels = np.array(labels)
    
    # 确保坐标在 0-10 范围内
    points = np.clip(points, 0.1, 9.9)
    
    # 打乱顺序
    indices = np.random.permutation(len(points))
    return points[indices], labels[indices]
    """生成笑脸形状的数据 - 修正嘴巴位置"""
    np.random.seed(42)
    
    # 精确计算各部分点数
    n_face = n_samples // 2
    n_eye = n_samples // 8
    n_mouth = n_samples - n_face - 2 * n_eye
    
    points = []
    labels = []
    
    # 1. 脸轮廓 (大圆)
    angles = np.random.uniform(0, 2 * np.pi, n_face)
    radii = np.random.uniform(3.5, 4.5, n_face)
    face_x = 5 + radii * np.cos(angles)
    face_y = 5 + radii * np.sin(angles)
    points.extend(np.column_stack([face_x, face_y]))
    labels.extend([0] * n_face)
    
    # 2. 左眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)
    left_eye_x = 3.5 + radii * np.cos(angles)
    left_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([left_eye_x, left_eye_y]))
    labels.extend([1] * n_eye)
    
    # 3. 右眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)
    right_eye_x = 6.5 + radii * np.cos(angles)
    right_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([right_eye_x, right_eye_y]))
    labels.extend([2] * n_eye)
    
    # 4. 嘴巴 - 尝试翻转Y坐标
    # angles = np.random.uniform(np.pi * 0.8, np.pi * 1.2, n_mouth)
    # radii = np.random.uniform(1.5, 2.5, n_mouth)
    
    # mouth_x = 5 + radii * np.cos(angles)
    # mouth_y = 4.5 - radii * np.sin(angles)  # 用减号而不是加号！
    
    # points.extend(np.column_stack([mouth_x, mouth_y]))
    # labels.extend([3] * n_mouth)
    
    
    angles = np.random.uniform(np.pi * 0.2, np.pi * 0.8, n_mouth)
    radii = np.random.uniform(2.0, 2.5, n_mouth)  # 调整半径范围
    mouth_x = 5 + radii * np.cos(angles)
    mouth_y = 5 + radii * np.sin(angles)  # 保持y坐标计算不变
    points.extend(np.column_stack([mouth_x, mouth_y]))
    labels.extend([3] * n_mouth)
    
    points = np.array(points)
    labels = np.array(labels)
    # 确保坐标在 0-10 范围内
    points = np.clip(points, 0.1, 9.9)
    
    # 打乱顺序
    indices = np.random.permutation(len(points))
    return points[indices], labels[indices]
    """生成笑脸形状的数据 - 修正版"""
    np.random.seed(42)

    # 精确计算各部分点数，避免整数除法误差
    n_face = n_samples // 2
    n_eye = n_samples // 8
    n_mouth = n_samples - n_face - 2 * n_eye  # 剩余点数给嘴巴
    
    points = []
    labels = []
    
    # 1. 脸轮廓 (大圆)
    angles = np.random.uniform(0, 2 * np.pi, n_face)
    radii = np.random.uniform(3.5, 4.5, n_face)  # 调整半径范围
    face_x = 5 + radii * np.cos(angles)
    face_y = 5 + radii * np.sin(angles)
    points.extend(np.column_stack([face_x, face_y]))
    labels.extend([0] * n_face)
    
    # 2. 左眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)  # 调整半径范围
    left_eye_x = 3.5 + radii * np.cos(angles)
    left_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([left_eye_x, left_eye_y]))
    labels.extend([1] * n_eye)
    
    # 3. 右眼 (小圆)
    angles = np.random.uniform(0, 2 * np.pi, n_eye)
    radii = np.random.uniform(0.4, 0.6, n_eye)  # 调整半径范围
    right_eye_x = 6.5 + radii * np.cos(angles)
    right_eye_y = 6 + radii * np.sin(angles)
    points.extend(np.column_stack([right_eye_x, right_eye_y]))
    labels.extend([2] * n_eye)
    
    # 4. 嘴巴 (向下弧形) - 修正这里！
    # 嘴巴应该是向下的弧形，角度从 0.2π 到 0.8π（下半圆）
    angles = np.random.uniform(np.pi * 0.2, np.pi * 0.8, n_mouth)
    radii = np.random.uniform(2.0, 2.5, n_mouth)  # 调整半径范围
    mouth_x = 5 + radii * np.cos(angles)
    mouth_y = 5 + radii * np.sin(angles)  # 保持y坐标计算不变
    points.extend(np.column_stack([mouth_x, mouth_y]))
    labels.extend([3] * n_mouth)
    
    points = np.array(points)
    labels = np.array(labels)
    
    # 确保坐标在 0-10 范围内
    points = np.clip(points, 0.1, 9.9)
    
    # 打乱顺序
    indices = np.random.permutation(len(points))
    return points[indices], labels[indices]     
def generate_spiral_data(n_samples):
    """生成螺旋分布数据"""
    np.random.seed(42)
    
    n_samples_per_class = n_samples // 3
    points = []
    labels = []
    
    # 生成3个螺旋
    for i in range(3):
        n = n_samples_per_class
        t = np.linspace(0, 4 * np.pi, n)
        r = t * 0.5 + np.random.normal(0, 0.1, n)
        
        x = 5 + r * np.cos(t + i * 2 * np.pi / 3)
        y = 5 + r * np.sin(t + i * 2 * np.pi / 3)
        
        points.extend(np.column_stack([x, y]))
        labels.extend([i] * n)
    
    points = np.array(points)
    labels = np.array(labels)
    
    # 打乱顺序
    indices = np.random.permutation(len(points))
    return points[indices], labels[indices]


def generate_anisotropic_data(n_samples):
    """生成异方差分布数据"""
    np.random.seed(42)
    
    # 生成变换后的高斯分布
    X, y = make_blobs(n_samples=n_samples, centers=3, random_state=42)
    
    # 应用各向异性变换
    transformation = [[0.6, -0.6], [-0.4, 0.8]]
    X_aniso = np.dot(X, transformation)
    
    # 移动到中心
    X_aniso = (X_aniso - X_aniso.mean(axis=0)) * 2 + np.array([5, 5])
    
    return X_aniso, y


def generate_noisy_data(n_samples):
    """生成带噪声的数据"""
    np.random.seed(42)
    
    # 生成正常聚类数据
    n_cluster_samples = n_samples * 3 // 4
    n_noise_samples = n_samples // 4
    
    # 生成3个高斯簇
    points, labels = make_blobs(
        n_samples=n_cluster_samples, 
        centers=3, 
        cluster_std=0.8, 
        random_state=42
    )
    
    # 添加噪声点
    noise_points = np.random.uniform(0, 10, (n_noise_samples, 2))
    noise_labels = np.full(n_noise_samples, -1)  # -1 表示噪声点
    
    all_points = np.vstack([points, noise_points])
    all_labels = np.concatenate([labels, noise_labels])
    
    # 打乱顺序
    indices = np.random.permutation(len(all_points))
    return all_points[indices], all_labels[indices]

def simulate_kmeans(points, k=3, init_method='random', custom_centroids=None):
    """模拟K-Means算法"""
    # 准备数据
    X = np.array([[p['x'], p['y']] for p in points])
    
    # 如果有自定义质心，使用自定义初始化
    if custom_centroids and len(custom_centroids) == k:
        init_points = np.array([[c['x'], c['y']] for c in custom_centroids])
        kmeans = KMeans(
            n_clusters=k,
            init=init_points,
            n_init=1,  # 使用自定义质心时只运行一次
            max_iter=100,
            random_state=42
        )
    else:
        # 运行K-Means
        kmeans = KMeans(
            n_clusters=k,
            init=init_method,
            n_init=10,
            max_iter=100,
            random_state=42
        )
    
    # 模拟迭代过程
    steps = []
    
    # 步骤1: 初始状态
    steps.append({
        'step': 1,
        'description': '初始数据点（未分类）',
        'points': [{'x': p['x'], 'y': p['y'], 'cluster': -1} for p in points],
        'centroids': [],
        'metrics': {}
    })
    
    # 如果有自定义质心，添加显示自定义质心的步骤
    if custom_centroids and len(custom_centroids) == k:
        steps.append({
            'step': 2,
            'description': '使用自定义质心位置',
            'points': [{'x': p['x'], 'y': p['y'], 'cluster': -1} for p in points],
            'centroids': [{'x': c['x'], 'y': c['y'], 'cluster': i} 
                         for i, c in enumerate(custom_centroids)],
            'metrics': {}
        })
    
    kmeans.fit(X)
    
    # 模拟几次迭代
    for i in range(min(5, kmeans.n_iter_)):
        # 这里简化了实际的K-Means迭代过程
        # 实际项目中应该实现完整的迭代跟踪
        step_description = f'迭代 {i + 1}: 分配点到质心并更新质心位置'
        if i == kmeans.n_iter_ - 1:
            step_description = '收敛完成 - 算法结束'
            
        steps.append({
            'step': len(steps) + 1,
            'description': step_description,
            'points': [{'x': p['x'], 'y': p['y'], 'cluster': int(l)} 
                      for p, l in zip(points, kmeans.labels_)],
            'centroids': [{'x': float(c[0]), 'y': float(c[1]), 'cluster': i} 
                         for i, c in enumerate(kmeans.cluster_centers_)],
            'metrics': {
                'inertia': float(kmeans.inertia_)
            }
        })
    
    # 计算性能指标
    silhouette = silhouette_score(X, kmeans.labels_)
    
    return {
        'steps': steps,
        'metrics': {
            'silhouette': round(silhouette, 4),
            'sse': round(kmeans.inertia_, 2),
            'iterations': kmeans.n_iter_
        }
    }

def simulate_dbscan(points, epsilon=0.5, min_samples=5):
    """模拟DBSCAN算法"""
    X = np.array([[p['x'], p['y']] for p in points])
    
    # 标准化数据
    X_scaled = StandardScaler().fit_transform(X)
    
    # 运行DBSCAN
    dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)
    
    # 模拟DBSCAN的执行步骤
    steps = []
    
    # 步骤1: 初始状态
    steps.append({
        'step': 1,
        'description': '初始数据点（未分类）',
        'points': [{'x': p['x'], 'y': p['y'], 'cluster': -1} for p in points],
        'metrics': {}
    })
    
    # 步骤2: 识别核心点
    core_points_mask = np.zeros(len(points), dtype=bool)
    for i in range(len(points)):
        distances = np.sqrt(np.sum((X_scaled - X_scaled[i])**2, axis=1))
        neighbors_count = np.sum(distances <= epsilon)
        core_points_mask[i] = neighbors_count >= min_samples
    
    steps.append({
        'step': 2,
        'description': '识别核心点（红色标记）',
        'points': [{
            'x': p['x'], 
            'y': p['y'], 
            'cluster': 0 if core_points_mask[i] else -1
        } for i, p in enumerate(points)],
        'metrics': {
            'core_points': int(np.sum(core_points_mask))
        }
    })
    
    # 步骤3: 聚类结果
    clustered_points = []
    for i, point in enumerate(points):
        clustered_points.append({
            'x': point['x'],
            'y': point['y'],
            'cluster': int(labels[i]),
            'originalCluster': point.get('originalCluster', -1)
        })
    
    steps.append({
        'step': 3,
        'description': 'DBSCAN聚类完成',
        'points': clustered_points,
        'metrics': {
            'clusters': len(set(labels)) - (1 if -1 in labels else 0),
            'noise_points': list(labels).count(-1)
        }
    })
    
    # 计算性能指标
    if len(set(labels)) > 1:
        silhouette = silhouette_score(X_scaled, labels)
    else:
        silhouette = -1
    
    return {
        'steps': steps,
        'metrics': {
            'silhouette': round(silhouette, 4) if silhouette != -1 else 'N/A',
            'clusters': len(set(labels)) - (1 if -1 in labels else 0),
            'noise_points': list(labels).count(-1)
        }
    }

def simulate_gmm(points, n_components=3, covariance_type='full', max_iter=100, tol=1e-3):
    """模拟高斯混合模型(GMM)算法"""
    X = np.array([[p['x'], p['y']] for p in points])
    
    # 运行GMM
    gmm = GaussianMixture(
        n_components=n_components,
        covariance_type=covariance_type,
        max_iter=max_iter,
        tol=tol,
        random_state=42
    )
    gmm.fit(X)
    labels = gmm.predict(X)
    probabilities = gmm.predict_proba(X)
    
    # 模拟GMM的执行步骤
    steps = []
    
    # 步骤1: 初始状态
    steps.append({
        'step': 1,
        'description': '初始数据点（未分类）',
        'points': [{'x': p['x'], 'y': p['y'], 'cluster': -1, 'probability': 0} for p in points],
        'centroids': [],
        'metrics': {}
    })
    
    # 步骤2: 初始化参数
    # 随机选择初始均值
    np.random.seed(42)
    indices = np.random.choice(len(X), n_components, replace=False)
    initial_means = X[indices]
    
    steps.append({
        'step': 2,
        'description': '初始化高斯分布参数',
        'points': [{'x': p['x'], 'y': p['y'], 'cluster': -1, 'probability': 0} for p in points],
        'centroids': [{'x': float(m[0]), 'y': float(m[1]), 'cluster': i} 
                     for i, m in enumerate(initial_means)],
        'metrics': {}
    })
    
    # 模拟EM算法迭代
    for i in range(min(5, gmm.n_iter_)):
        # 这里简化了实际的EM迭代过程
        step_description = f'EM迭代 {i + 1}: 更新高斯分布参数'
        if i == gmm.n_iter_ - 1:
            step_description = '收敛完成 - 算法结束'
            
        # 为每个点分配簇和概率
        gmm_iter = GaussianMixture(
            n_components=n_components,
            covariance_type=covariance_type,
            max_iter=i + 1,
            tol=tol,
            random_state=42
        )
        gmm_iter.fit(X)
        labels_iter = gmm_iter.predict(X)
        probs_iter = gmm_iter.predict_proba(X)
        
        step_points = []
        for j, point in enumerate(points):
            max_prob = np.max(probs_iter[j]) if j < len(probs_iter) else 0
            step_points.append({
                'x': point['x'],
                'y': point['y'],
                'cluster': int(labels_iter[j]) if j < len(labels_iter) else -1,
                'probability': float(max_prob),
                'originalCluster': point.get('originalCluster', -1)
            })
        
        steps.append({
            'step': len(steps) + 1,
            'description': step_description,
            'points': step_points,
            'centroids': [{'x': float(m[0]), 'y': float(m[1]), 'cluster': i} 
                         for i, m in enumerate(gmm_iter.means_)],
            'metrics': {
                'log_likelihood': float(gmm_iter.lower_bound_)
            }
        })
    
    # 最终结果
    final_points = []
    for i, point in enumerate(points):
        max_prob = np.max(probabilities[i]) if i < len(probabilities) else 0
        final_points.append({
            'x': point['x'],
            'y': point['y'],
            'cluster': int(labels[i]),
            'probability': float(max_prob),
            'originalCluster': point.get('originalCluster', -1)
        })
    
    # 计算性能指标
    silhouette = silhouette_score(X, labels)
    bic = gmm.bic(X)
    aic = gmm.aic(X)
    
    return {
        'steps': steps,
        'metrics': {
            'silhouette': round(silhouette, 4),
            'bic': round(bic, 2),
            'aic': round(aic, 2),
            'iterations': gmm.n_iter_,
            'converged': gmm.converged_
        }
    }

def get_supported_data_types():
    """获取支持的数据类型"""
    return [
        {
            'value': 'uniform',
            'label': '均匀分布',
            'description': '数据点在整个空间均匀分布',
            'supported_algorithms': ['kmeans', 'dbscan', 'gmm']
        },
        {
            'value': 'gaussian',
            'label': '高斯分布',
            'description': '数据点呈高斯分布，形成自然簇',
            'supported_algorithms': ['kmeans', 'gmm']
        },
        {
            'value': 'moons',
            'label': '月牙分布',
            'description': '数据点形成月牙形结构',
            'supported_algorithms': ['dbscan']
        },
        {
            'value': 'circles',
            'label': '环形分布',
            'description': '数据点形成环形结构',
            'supported_algorithms': ['dbscan']
        },
        {
            'value': 'smiley',
            'label': '笑脸分布',
            'description': '数据点形成笑脸形状，测试复杂结构识别',
            'supported_algorithms': ['dbscan', 'gmm']
        },
        {
            'value': 'spiral',
            'label': '螺旋分布',
            'description': '数据点形成螺旋结构，测试非线性分离',
            'supported_algorithms': ['dbscan']
        },
        {
            'value': 'anisotropic',
            'label': '异方差分布',
            'description': '不同方向方差不同的高斯分布',
            'supported_algorithms': ['kmeans', 'gmm']
        },
        {
            'value': 'noisy',
            'label': '噪声分布',
            'description': '包含大量噪声点的数据集',
            'supported_algorithms': ['dbscan']
        }
    ]

def get_supported_centroid_methods():
    """获取支持的质心初始化方法"""
    return [
        {
            'value': 'random',
            'label': '随机选择',
            'description': '随机选择K个点作为初始质心',
            'supported_algorithms': ['kmeans']
        },
        {
            'value': 'k-means++',
            'label': 'K-Means++',
            'description': '使用K-Means++算法优化初始质心选择',
            'supported_algorithms': ['kmeans']
        },
        {
            'value': 'custom',
            'label': '自定义',
            'description': '手动选择质心位置',
            'supported_algorithms': ['kmeans']
        }
    ]