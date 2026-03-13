"""数据管理相关路由

提供数据管理相关的API接口，包括数据统计、老人信息、健康记录、服务记录等
"""

from flask import Blueprint, jsonify, request, send_file, current_app
import sqlite3
import pandas as pd
import io

# 创建蓝图
bp = Blueprint('data', __name__, url_prefix='/api/data')

# 数据库连接函数
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/stats')
def get_data_stats():
    """获取数据统计信息"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 统计老人总数
        cursor.execute('SELECT COUNT(*) FROM senior')
        senior_count = cursor.fetchone()[0]
        
        # 统计健康记录数
        cursor.execute('SELECT COUNT(*) FROM health_record')
        health_records = cursor.fetchone()[0]
        
        # 统计服务记录数
        cursor.execute('SELECT COUNT(*) FROM service_log')
        service_logs = cursor.fetchone()[0]
        
        # 统计社区数量
        cursor.execute('SELECT COUNT(DISTINCT community_id) FROM senior')
        communities = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'senior_count': senior_count,
            'health_records': health_records,
            'service_logs': service_logs,
            'communities': communities
        })
    except Exception as e:
        print(f"获取数据统计失败: {e}")
        return jsonify({'error': '获取数据统计失败'}), 500

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
        query = 'SELECT * FROM senior'
        params = []
        
        if community:
            query += ' WHERE community_id = ?'
            params.append(community)
        
        # 获取总数
        count_query = 'SELECT COUNT(*) FROM senior'
        if community:
            count_query += ' WHERE community_id = ?'
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 分页查询
        offset = (page - 1) * page_size
        query += ' LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        seniors = [dict(row) for row in cursor.fetchall()]
        
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
            query += ' WHERE date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        elif start_date:
            query += ' WHERE date >= ?'
            params.append(start_date)
        elif end_date:
            query += ' WHERE date <= ?'
            params.append(end_date)
        
        # 获取总数
        count_query = 'SELECT COUNT(*) FROM health_record'
        if start_date and end_date:
            count_query += ' WHERE date BETWEEN ? AND ?'
        elif start_date:
            count_query += ' WHERE date >= ?'
        elif end_date:
            count_query += ' WHERE date <= ?'
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
        query = 'SELECT * FROM service_log'
        params = []
        
        if service_type:
            query += ' WHERE service_type = ?'
            params.append(service_type)
        
        # 获取总数
        count_query = 'SELECT COUNT(*) FROM service_log'
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
        
        # 读取数据
        seniors_df = pd.read_sql('SELECT * FROM senior', conn)
        health_df = pd.read_sql('SELECT * FROM health_record', conn)
        service_df = pd.read_sql('SELECT * FROM service_log', conn)
        
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
        print(f"导出数据失败: {e}")
        return jsonify({'error': '导出数据失败'}), 500

@bp.route('/communities')
def get_communities():
    """获取社区列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询所有社区
        cursor.execute('SELECT DISTINCT community_id FROM senior')
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
        cursor.execute('SELECT DISTINCT service_type FROM service_log')
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
