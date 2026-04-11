"""预测相关路由

处理服务需求预测、趋势等API
"""

from flask import Blueprint, jsonify, request
from app.services.prediction_service import PredictionService

# 创建蓝图
bp = Blueprint('prediction', __name__, url_prefix='/api/prediction')

# 预测服务实例
prediction_service = PredictionService()

@bp.route('/trend')
def get_prediction_trend():
    """预测趋势 API
    
    提供服务需求预测趋势数据的API接口，返回JSON格式数据
    
    参数：
    - community: 社区名称，默认值为'社区A'
    - service: 服务类型，默认值为'助餐'
    - days: 预测天数，默认值为7天
    - model: 预测模型，默认值为'random_forest'
    - confidence: 置信度，默认值为0.9
    - seasonal: 季节性分析，默认值为'none'
    """
    try:
        community_id = request.args.get('community', '社区A')  # 社区名称，默认社区A
        service_type = request.args.get('service', '助餐')      # 服务类型，默认助餐
        days = int(request.args.get('days', 7))                # 预测天数，默认7天
        model = request.args.get('model', 'random_forest')      # 预测模型
        confidence = float(request.args.get('confidence', 0.9))  # 置信度
        seasonal = request.args.get('seasonal', 'none')         # 季节性分析
        data = prediction_service.get_prediction_trend(community_id, service_type, days, model, confidence, seasonal)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/resource/recommendations')
def get_resource_recommendations():
    """资源配置建议 API
    
    提供资源配置建议数据的API接口，返回JSON格式数据
    
    参数：
    - community: 社区名称，默认值为None（所有社区）
    """
    try:
        community = request.args.get('community', None)  # 社区名称，默认所有社区
        data = prediction_service.get_resource_recommendations(community)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/model/metrics')
def get_model_metrics():
    """模型评估指标 API
    
    提供模型评估指标数据的API接口，返回JSON格式数据
    """
    try:
        data = prediction_service.get_model_metrics()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/model/comparison')
def get_model_comparison():
    """模型对比 API
    
    提供模型对比数据的API接口，返回JSON格式数据
    """
    try:
        data = prediction_service.get_model_comparison()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/model/train', methods=['POST'])
def train_model():
    """模型训练 API
    
    训练预测模型的API接口，返回JSON格式数据
    """
    try:
        data = prediction_service.train_model()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/anomalies')
def get_anomalies():
    """异常检测 API
    
    提供异常检测结果的API接口，返回JSON格式数据
    """
    try:
        data = prediction_service.detect_anomalies()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/export')
def export_prediction_data():
    """导出预测数据 API
    
    导出预测数据的API接口，返回JSON格式数据
    
    参数：
    - community: 社区名称，默认值为'社区A'
    - service: 服务类型，默认值为'助餐'
    - days: 预测天数，默认值为7天
    """
    try:
        community_id = request.args.get('community', '社区A')  # 社区名称，默认社区A
        service_type = request.args.get('service', '助餐')      # 服务类型，默认助餐
        days = int(request.args.get('days', 7))                # 预测天数，默认7天
        data = prediction_service.export_prediction_data(community_id, service_type, days)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
