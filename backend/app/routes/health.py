"""健康相关路由

处理健康状态分布、趋势等API
"""

from flask import Blueprint, jsonify
from app.services.health_service import HealthService

# 创建蓝图
bp = Blueprint('health', __name__, url_prefix='/api/health')

# 健康服务实例
health_service = HealthService()

@bp.route('/distribution')
def get_health_distribution():
    """健康状态分布 API
    
    提供健康状态分布数据的API接口，返回JSON格式数据
    """
    try:
        data = health_service.get_health_distribution()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/distribution/age')
def get_health_distribution_by_age():
    """按年龄段分析健康状态分布 API
    
    提供按年龄段分析的健康状态分布数据的API接口，返回JSON格式数据
    """
    try:
        data = health_service.get_health_distribution_by_age()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/trend')
def get_health_trend():
    """健康状态趋势 API
    
    提供健康状态趋势数据的API接口，返回JSON格式数据
    """
    try:
        data = health_service.get_health_trend()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
