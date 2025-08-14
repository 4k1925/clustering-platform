# routes/cluster.py
from flask import Blueprint, jsonify, request
import numpy as np
from sklearn.cluster import KMeans

bp = Blueprint('cluster', __name__)

@bp.route('/kmeans', methods=['POST'])
def kmeans():
    data = request.json
    points = np.array(data['points'])
    kmeans = KMeans(n_clusters=data.get('k', 3))
    labels = kmeans.fit_predict(points)
    return jsonify({
        'labels': labels.tolist(),
        'centers': kmeans.cluster_centers_.tolist()
    })