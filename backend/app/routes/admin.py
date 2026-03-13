"""管理相关路由

处理数据生成、清洗、模型训练等管理功能
"""

from flask import Blueprint, jsonify
from app.services.admin_service import AdminService

# 创建蓝图
bp = Blueprint('admin', __name__, url_prefix='/api')

# 管理服务实例
admin_service = AdminService()

@bp.route('/clean', methods=['POST'])
def clean_data():
    """数据清洗接口
    
    提供数据清洗功能的API接口，返回清洗统计数据
    """
    try:
        stats = admin_service.clean_data()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/train', methods=['POST'])
def train_model_api():
    """训练模型接口
    
    提供模型训练功能的API接口，返回模型评估指标
    """
    try:
        metrics = admin_service.train_model()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/generate', methods=['POST'])
def generate_data():
    """重新生成模拟数据接口
    
    提供重新生成模拟数据功能的API接口
    """
    try:
        admin_service.generate_data()
        return jsonify({'message': '模拟数据生成完成！'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
