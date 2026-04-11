"""指标相关路由

处理关键指标等API
"""

from flask import Blueprint, jsonify
from app.services.data_service import DataService
from app.utils.database import db

# 创建蓝图
bp = Blueprint('indicator', __name__, url_prefix='/api/key')

@bp.route('/indicators')
def get_key_indicators_api():
    """关键指标 API
    
    提供关键指标数据的API接口，返回JSON格式数据
    """
    try:
        data_service = DataService()
        data = data_service.get_data_stats()

        # map fields to frontend expected keys
        service_count = data.get('service_logs', 0)

        # 计算平均满意度
        avg_sat_res = db.execute('SELECT AVG(satisfaction) FROM service_record')
        avg_satisfaction = round(float(avg_sat_res[0][0]), 1) if avg_sat_res and avg_sat_res[0][0] else 0

        # 计算高危人数（health_status 包含 高危 关键字）
        high_risk_res = db.execute("SELECT COUNT(*) FROM health_record WHERE health_status LIKE '%高危%'")
        high_risk_count = high_risk_res[0][0] if high_risk_res else 0

        result = {
            'senior_count': data.get('senior_count', 0),
            'service_count': service_count,
            'avg_satisfaction': avg_satisfaction,
            'high_risk_count': high_risk_count,
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
