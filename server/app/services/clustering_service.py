# server/app/services/clustering_service.py
from sklearn.cluster import KMeans
import numpy as np

def run_kmeans(data, n_clusters=3):
    """基础K-means实现"""
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(data)
    return {
        'labels': kmeans.labels_.tolist(),
        'centers': kmeans.cluster_centers_.tolist()
    }