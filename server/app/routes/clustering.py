# server/app/routes/clustering.py
from flask import Blueprint
from ..services.clustering_service import run_kmeans  # 确保路径正确
from flask import request, jsonify

clustering_bp = Blueprint('clustering', __name__)

@clustering_bp.route('/kmeans', methods=['POST'])
def kmeans():
    # 示例实现
    data = request.json.get('data')
    result = run_kmeans(data)
    return jsonify(result)