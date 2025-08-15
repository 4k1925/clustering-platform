import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.datasets import make_blobs
import json

class ClusteringService:
    @staticmethod
    def generate_sample_data(n_samples=300, n_features=2, centers=3):
        """生成用于聚类的样本数据"""
        X, y = make_blobs(n_samples=n_samples, n_features=n_features, centers=centers)
        return X.tolist(), y.tolist()
    
    @staticmethod
    def perform_kmeans(X, n_clusters=3, max_iter=300):
        """执行K-means聚类"""
        kmeans = KMeans(n_clusters=n_clusters, max_iter=max_iter)
        labels = kmeans.fit_predict(X)
        centroids = kmeans.cluster_centers_.tolist()
        return {
            'labels': labels.tolist(),
            'centroids': centroids,
            'algorithm': 'kmeans'
        }
    
    @staticmethod
    def perform_dbscan(X, eps=0.5, min_samples=5):
        """执行DBSCAN聚类"""
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)
        return {
            'labels': labels.tolist(),
            'algorithm': 'dbscan'
        }
    
    @staticmethod
    def perform_hierarchical(X, n_clusters=3, linkage='ward'):
        """执行层次聚类"""
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
        labels = hierarchical.fit_predict(X)
        return {
            'labels': labels.tolist(),
            'algorithm': 'hierarchical'
        }