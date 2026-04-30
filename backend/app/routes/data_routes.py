"""数据管理相关路由

提供数据管理相关的API接口，严格遵循角色权责划分
"""

from flask import Blueprint, jsonify, request, current_app
from app.services.data_service import DataService
from app.utils.database import db
from functools import wraps
import traceback

# 创建蓝图
bp = Blueprint('data', __name__, url_prefix='/api/data')

# 数据服务实例
data_service = DataService()

def roles_required(*roles):
    """角色验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 优先从 Header 获取，兼容参数
            role = request.headers.get('X-User-Role') or request.args.get('role')
            if not role:
                return jsonify({'error': '未授权'}), 401
            if role not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/stats')
def get_data_stats_api():
    """获取数据统计概览"""
    try:
        stats = data_service.get_data_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- 社区管理 ---
@bp.route('/communities', methods=['GET'])
def get_communities_api():
    return jsonify(data_service.get_communities())

@bp.route('/communities', methods=['POST'])
@roles_required('institution')
def add_community_api():
    try:
        data_service.add_community(request.json)
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/communities/<string:community_id>', methods=['PUT'])
@roles_required('institution')
def update_community_api(community_id):
    try:
        data_service.update_community(community_id, request.json)
        return jsonify({'message': '更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/communities/<string:community_id>', methods=['DELETE'])
@roles_required('institution')
def delete_community_api(community_id):
    try:
        data_service.delete_community(community_id)
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 老人管理 ---
@bp.route('/seniors', methods=['GET'])
def get_seniors_api():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        community = request.args.get('community', '')
        return jsonify(data_service.get_seniors(page, page_size, community))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/seniors', methods=['POST'])
@roles_required('institution', 'caregiver')
def add_elderly_api():
    try:
        data_service.add_elderly(request.json)
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/seniors/<string:elderly_id>', methods=['PUT'])
@roles_required('institution', 'caregiver')
def update_elderly_api(elderly_id):
    try:
        data_service.update_elderly(elderly_id, request.json)
        return jsonify({'message': '更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/seniors/<string:elderly_id>', methods=['DELETE'])
@roles_required('institution')
def delete_elderly_api(elderly_id):
    try:
        data_service.delete_elderly(elderly_id)
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 护工管理 ---
@bp.route('/caregivers', methods=['GET'])
def get_caregivers_api():
    community_id = request.args.get('community_id')
    return jsonify(data_service.get_caregivers(community_id))

@bp.route('/caregivers', methods=['POST'])
@roles_required('institution')
def add_caregiver_api():
    try:
        data_service.add_caregiver(request.json)
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/caregivers/<string:caregiver_id>', methods=['PUT'])
@roles_required('institution')
def update_caregiver_api(caregiver_id):
    try:
        data_service.update_caregiver(caregiver_id, request.json)
        return jsonify({'message': '更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/caregivers/<string:caregiver_id>', methods=['DELETE'])
@roles_required('institution')
def delete_caregiver_api(caregiver_id):
    try:
        data_service.delete_caregiver(caregiver_id)
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 排班管理 ---
@bp.route('/schedules', methods=['GET'])
def get_schedules_api():
    caregiver_id = request.args.get('caregiver_id')
    elderly_id = request.args.get('elderly_id')
    return jsonify(data_service.get_schedules(caregiver_id, elderly_id))

@bp.route('/schedules', methods=['POST'])
@roles_required('institution')
def add_schedule_api():
    try:
        data_service.add_schedule(request.json)
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@roles_required('institution')
def update_schedule_api(schedule_id):
    try:
        data_service.update_schedule(schedule_id, request.json)
        return jsonify({'message': '更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@roles_required('institution')
def delete_schedule_api(schedule_id):
    try:
        data_service.delete_schedule(schedule_id)
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 健康记录 ---
@bp.route('/health-records', methods=['GET'])
def get_health_records_api():
    """获取健康记录列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        return jsonify(data_service.get_health_records(page, page_size, start_date, end_date))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/health-records', methods=['POST'])
@roles_required('caregiver')
def add_health_record_api():
    """新增健康记录"""
    try:
        data_service.add_health_record(request.json)
        return jsonify({'message': '上报成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/health-records/<int:record_id>', methods=['PUT'])
@roles_required('caregiver')
def update_health_record_api(record_id):
    """更新健康记录"""
    try:
        data_service.update_health_record(record_id, request.json)
        return jsonify({'message': '更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/health-records/<int:record_id>', methods=['DELETE'])
@roles_required('caregiver')
def delete_health_record_api(record_id):
    """删除健康记录"""
    try:
        data_service.delete_health_record(record_id)
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 服务记录 ---
@bp.route('/service-records', methods=['GET'])
def get_service_records_api():
    """获取服务记录列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        service_type = request.args.get('service_type', '')
        return jsonify(data_service.get_service_records(page, page_size, service_type))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/service-records', methods=['POST'])
@roles_required('caregiver')
def add_service_record_api():
    """新增服务记录"""
    try:
        data_service.add_service_record(request.json)
        return jsonify({'message': '提交成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/service-records/<int:record_id>', methods=['PUT'])
@roles_required('caregiver')
def update_service_record_api(record_id):
    """更新服务记录"""
    try:
        data_service.update_service_record(record_id, request.json)
        return jsonify({'message': '更新成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/service-records/<int:record_id>', methods=['DELETE'])
@roles_required('caregiver')
def delete_service_record_api(record_id):
    """删除服务记录"""
    try:
        data_service.delete_service_record(record_id)
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 服务类型列表 ---
@bp.route('/services', methods=['GET'])
def get_services_api():
    """获取服务类型列表 - 所有角色可访问"""
    try:
        # 从 service_record 表中获取所有不重复的服务类型
        result = db.execute("SELECT DISTINCT service_type FROM service_record ORDER BY service_type")
        services = [row[0] for row in result]
        # 如果数据库中没有数据,返回默认的服务类型列表
        if not services:
            services = ['助餐', '助医', '保洁', '陪护', '康复']
        return jsonify(services)
    except Exception as e:
        # 出错时返回默认服务类型
        return jsonify(['助餐', '助医', '保洁', '陪护', '康复'])

# --- 预测与报表 ---
@bp.route('/predictions', methods=['GET'])
def get_predictions_api():
    """获取预测需求结果 - 所有角色可访问"""
    community_id = request.args.get('community_id')
    service_type = request.args.get('service_type')
    return jsonify(data_service.get_predictions(community_id, service_type))

@bp.route('/reports/community', methods=['GET'])
@roles_required('institution', 'regulatory')
def get_community_reports_api():
    community_id = request.args.get('community_id')
    return jsonify(data_service.get_community_stats(community_id))
