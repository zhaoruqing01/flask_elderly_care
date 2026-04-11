"""服务相关路由

处理服务使用频次、满意度等API
"""

from flask import Blueprint, jsonify
from app.services.service_service import ServiceService

# 创建蓝图
bp = Blueprint('service', __name__, url_prefix='/api/service')

# 服务服务实例
service_service = ServiceService()

@bp.route('/frequency')
def get_service_frequency():
    """服务使用频次 API
    
    提供服务使用频次数据的API接口，返回JSON格式数据
    """
    try:
        data = service_service.get_service_frequency()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/frequency/community')
def get_service_frequency_by_community():
    """按社区分析服务使用频次 API
    
    提供按社区分析的服务使用频次数据的API接口，返回JSON格式数据
    """
    try:
        data = service_service.get_service_frequency_by_community()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/satisfaction')
def get_service_satisfaction():
    """服务满意度 API
    
    提供服务满意度数据的API接口，返回JSON格式数据
    """
    try:
        data = service_service.get_service_satisfaction()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/trend')
def get_service_trend():
    """服务使用趋势 API
    
    提供服务使用趋势数据的API接口，返回JSON格式数据
    """
    try:
        data = service_service.get_service_trend()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
