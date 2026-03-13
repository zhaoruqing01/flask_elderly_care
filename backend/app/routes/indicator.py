"""指标相关路由

处理关键指标等API
"""

from flask import Blueprint, jsonify
from analysis import get_key_indicators

# 创建蓝图
bp = Blueprint('indicator', __name__, url_prefix='/api/key')

@bp.route('/indicators')
def get_key_indicators_api():
    """关键指标 API
    
    提供关键指标数据的API接口，返回JSON格式数据
    """
    try:
        data = get_key_indicators()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
