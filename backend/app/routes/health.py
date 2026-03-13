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

@bp.route('/recommendations')
def get_health_recommendations():
    """健康建议 API
    
    提供健康照护建议数据的API接口，返回JSON格式数据
    """
    try:
        # 健康建议数据
        recommendations = [
            {
                "category": "饮食",
                "title": "合理膳食",
                "content": "建议每日摄入多样化的食物，包括谷物、蔬菜、水果、蛋白质和奶制品，控制盐和油脂的摄入",
                "target": "所有老人"
            },
            {
                "category": "运动",
                "title": "适量运动",
                "content": "建议每天进行30分钟左右的轻度运动，如散步、太极拳等，增强体质",
                "target": "健康良好老人"
            },
            {
                "category": "监测",
                "title": "定期体检",
                "content": "建议每半年进行一次全面体检，及时发现和处理健康问题",
                "target": "所有老人"
            },
            {
                "category": "照护",
                "title": "专人照护",
                "content": "对于高危老人，建议安排专人照护，定期监测健康状况",
                "target": "高危老人"
            },
            {
                "category": "用药",
                "title": "规范用药",
                "content": "建议按照医嘱规范用药，不要自行增减药量",
                "target": "有慢性疾病老人"
            },
            {
                "category": "心理",
                "title": "心理健康",
                "content": "建议保持积极乐观的心态，多参加社交活动，避免孤独感",
                "target": "所有老人"
            }
        ]
        return jsonify({'data': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
