from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services.clustering_service import ClusteringService

clustering_bp = Blueprint('clustering', __name__)

@clustering_bp.route('/generate-data', methods=['GET'])
@login_required
def generate_data():
    try:
        X, y = ClusteringService.generate_sample_data()
        return jsonify({
            'data': X,
            'labels': y
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clustering_bp.route('/kmeans', methods=['POST'])
@login_required
def perform_kmeans():
    data = request.get_json()
    try:
        result = ClusteringService.perform_kmeans(
            data.get('data'),
            n_clusters=data.get('n_clusters', 3)
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clustering_bp.route('/dbscan', methods=['POST'])
@login_required
def perform_dbscan():
    data = request.get_json()
    try:
        result = ClusteringService.perform_dbscan(
            data.get('data'),
            eps=data.get('eps', 0.5),
            min_samples=data.get('min_samples', 5)
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clustering_bp.route('/gmm', methods=['POST'])
@login_required
def perform_gmm():
    data = request.get_json()
    try:
        result = ClusteringService.perform_gmm(
            data.get('data'),
            n_components=data.get('n_components', 3),
            covariance_type=data.get('covariance_type', 'full'),
            random_state=data.get('random_state', 42)
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
