from flask import Blueprint, request, jsonify
from ..services.clustering_service import run_kmeans

clustering_bp = Blueprint('clustering', __name__)

@clustering_bp.route('/kmeans', methods=['POST'])
def kmeans():
    data = request.get_json()
    result = run_kmeans(data['points'], data['k'])
    return jsonify(result)