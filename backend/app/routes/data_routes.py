"""数据管理相关路由

提供数据管理相关的API接口，包括数据统计、老人信息、健康记录、服务记录等
"""

from flask import Blueprint, jsonify, request, send_file, current_app
import sqlite3
import pandas as pd
import io
import traceback

from app.services.data_service import DataService
from functools import wraps

# 创建蓝图
bp = Blueprint('data', __name__, url_prefix='/api/data')

# 数据服务实例
data_service = DataService()

def roles_required(*roles):
    """角色验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 这里暂时通过参数模拟，实际应配合Token/Session
            role = request.args.get('role') or request.headers.get('X-User-Role')
            if not role:
                return jsonify({'error': '未授权'}), 401
            if role not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/stats')
def get_data_stats_api():
    """获取数据统计信息"""
    try:
        stats = data_service.get_data_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- 社区管理接口 ---
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

# --- 老人管理接口 ---
@bp.route('/seniors', methods=['POST'])
@roles_required('institution', 'caregiver')
def add_elderly_api():
    try:
        data_service.add_elderly(request.json)
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 护工管理接口 ---
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

# --- 排班管理接口 ---
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

# --- 健康记录接口 ---
@bp.route('/health-records', methods=['POST'])
@roles_required('caregiver')
def add_health_record_api():
    try:
        data_service.add_health_record(request.json)
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- 服务记录接口 ---
@bp.route('/service-records', methods=['POST'])
@roles_required('caregiver')
def add_service_record_api():
    try:
        data_service.add_service_record(request.json)
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/seniors')
def get_seniors():
    """获取老人数据，支持分页和社区筛选"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        community = request.args.get('community', '')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 构建查询
        query = 'SELECT * FROM elderly'
        params = []
        
        if community:
            query += ' WHERE community_id = ?'
            params.append(community)
        
        # 获取总数
        count_query = 'SELECT COUNT(*) FROM elderly'
        if community:
            count_query += ' WHERE community_id = ?'
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 分页查询
        offset = (page - 1) * page_size
        query += ' LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        seniors = []
        
        for row in cursor.fetchall():
            senior = dict(row)
            senior_id = senior.get('elderly_id') or senior.get('id')
            
            # 获取老人的最新健康状态
            health_query = '''
            SELECT health_status 
            FROM health_record 
            WHERE elderly_id = ? 
            ORDER BY record_date DESC 
            LIMIT 1
            '''
            cursor.execute(health_query, (senior_id,))
            health_result = cursor.fetchone()
            senior['health_status'] = health_result[0] if health_result else '未知'
            
            # 获取老人的服务次数
            service_count_query = 'SELECT COUNT(*) FROM service_record WHERE elderly_id = ?'
            cursor.execute(service_count_query, (senior_id,))
            service_count_result = cursor.fetchone()
            senior['service_count'] = service_count_result[0] if service_count_result else 0
            
            # 获取老人的平均满意度
            satisfaction_query = 'SELECT AVG(satisfaction) FROM service_record WHERE elderly_id = ?'
            cursor.execute(satisfaction_query, (senior_id,))
            satisfaction_result = cursor.fetchone()
            senior['avg_satisfaction'] = round(float(satisfaction_result[0]), 1) if satisfaction_result and satisfaction_result[0] else 0
            
            seniors.append(senior)
        
        conn.close()
        
        return jsonify({
            'items': seniors,
            'total': total
        })
    except Exception as e:
        print(f"获取老人数据失败: {e}")
        return jsonify({'error': '获取老人数据失败'}), 500

@bp.route('/health-records')
def get_health_records():
    """获取健康记录，支持分页和日期范围筛选"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 构建查询
        query = 'SELECT * FROM health_record'
        params = []
        
        if start_date and end_date:
            query += ' WHERE record_date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        elif start_date:
            query += ' WHERE record_date >= ?'
            params.append(start_date)
        elif end_date:
            query += ' WHERE record_date <= ?'
            params.append(end_date)
        
        # 获取总数
        count_query = 'SELECT COUNT(*) FROM health_record'
        if start_date and end_date:
            count_query += ' WHERE record_date BETWEEN ? AND ?'
        elif start_date:
            count_query += ' WHERE record_date >= ?'
        elif end_date:
            count_query += ' WHERE record_date <= ?'
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 分页查询
        offset = (page - 1) * page_size
        query += ' LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        records = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'items': records,
            'total': total
        })
    except Exception as e:
        print(f"获取健康记录失败: {e}")
        return jsonify({'error': '获取健康记录失败'}), 500

@bp.route('/service-records')
def get_service_records():
    """获取服务记录，支持分页和服务类型筛选"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        service_type = request.args.get('service_type')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 构建查询
        query = 'SELECT * FROM service_record'
        params = []

        if service_type:
            query += ' WHERE service_type = ?'
            params.append(service_type)

        # 获取总数
        count_query = 'SELECT COUNT(*) FROM service_record'
        if service_type:
            count_query += ' WHERE service_type = ?'
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 分页查询
        offset = (page - 1) * page_size
        query += ' LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        records = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'items': records,
            'total': total
        })
    except Exception as e:
        print(f"获取服务记录失败: {e}")
        return jsonify({'error': '获取服务记录失败'}), 500

@bp.route('/export')
def export_data():
    """导出数据为Excel文件"""
    try:
        conn = get_db()
        
        # 读取数据，兼容多套表名
        def table_exists(name):
            cur = conn.cursor()
            try:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
                return cur.fetchone() is not None
            finally:
                cur.close()

        def read_prefer(names, default_columns=None):
            # names: list of candidate table names in order
            for n in names:
                if table_exists(n):
                    try:
                        return pd.read_sql(f'SELECT * FROM {n}', conn)
                    except Exception:
                        # try next
                        continue
            # 返回空的 DataFrame 作为兜底
            if default_columns:
                return pd.DataFrame(columns=default_columns)
            return pd.DataFrame()

        seniors_df = read_prefer(['elderly', 'seniors', 'senior'], default_columns=['elderly_id', 'name', 'age', 'gender', 'community_id'])
        health_df = read_prefer(['health_record', 'health_records', 'health_log'], default_columns=['elderly_id', 'record_date', 'sbp', 'dbp', 'blood_sugar', 'heart_rate', 'health_status'])
        service_df = read_prefer(['service_record', 'service_records', 'service_log'], default_columns=['elderly_id', 'service_date', 'service_type', 'duration', 'satisfaction', 'community_id'])

        conn.close()
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            seniors_df.to_excel(writer, sheet_name='老人信息', index=False)
            health_df.to_excel(writer, sheet_name='健康记录', index=False)
            service_df.to_excel(writer, sheet_name='服务记录', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='elderly_care_data.xlsx'
        )
    except Exception as e:
        tb = traceback.format_exc()
        print(f"导出数据失败: {e}\n{tb}")
        # 在开发环境返回详细堆栈，便于定位问题；生产可改为简短信息
        return jsonify({'error': '导出数据失败', 'traceback': tb}), 500

@bp.route('/communities')
def get_communities():
    """获取社区列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询所有社区
        cursor.execute('SELECT DISTINCT community_id FROM elderly')
        communities = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # 如果没有社区数据，返回默认社区列表
        if not communities:
            communities = ['社区A', '社区B', '社区C', '社区D', '社区E']
        
        return jsonify(communities)
    except Exception as e:
        print(f"获取社区列表失败: {e}")
        # 返回默认社区列表作为 fallback
        return jsonify(['社区A', '社区B', '社区C', '社区D', '社区E'])

@bp.route('/services')
def get_services():
    """获取服务类型列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询所有服务类型
        cursor.execute('SELECT DISTINCT service_type FROM service_record')
        services = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # 如果没有服务类型数据，返回默认服务类型列表
        if not services:
            services = ['助餐', '助医', '保洁', '陪护', '康复']
        
        return jsonify(services)
    except Exception as e:
        print(f"获取服务类型列表失败: {e}")
        # 返回默认服务类型列表作为 fallback
        return jsonify(['助餐', '助医', '保洁', '陪护', '康复'])
