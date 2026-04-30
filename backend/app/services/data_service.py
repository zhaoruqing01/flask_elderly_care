"""数据服务模块

处理数据管理相关的业务逻辑
"""

import sqlite3
import pandas as pd
from app.utils.database import db

class DataService:
    """数据服务类"""
    
    def get_data_stats(self):
        """获取数据统计信息"""
        senior_count = db.execute('SELECT COUNT(*) FROM elderly')[0][0]
        health_records = db.execute('SELECT COUNT(*) FROM health_record')[0][0]
        service_logs = db.execute('SELECT COUNT(*) FROM service_record')[0][0]
        communities = db.execute('SELECT COUNT(*) FROM community')[0][0]
        caregivers = db.execute('SELECT COUNT(*) FROM caregiver')[0][0]
        
        return {
            'senior_count': senior_count,
            'health_records': health_records,
            'service_logs': service_logs,
            'communities': communities,
            'caregivers': caregivers
        }

    # --- 社区管理 ---
    def get_communities(self):
        """获取所有社区"""
        query = "SELECT community_id, name, total_population, elderly_population FROM community"
        result = db.execute(query)
        return [{'community_id': r[0], 'name': r[1], 'total_population': r[2], 'elderly_population': r[3]} for r in result]

    def add_community(self, data):
        """新增社区"""
        query = "INSERT INTO community (community_id, name, total_population, elderly_population) VALUES (?, ?, ?, ?)"
        db.execute(query, (data['community_id'], data['name'], data['total_population'], data['elderly_population']))

    def update_community(self, community_id, data):
        """更新社区"""
        query = "UPDATE community SET name=?, total_population=?, elderly_population=? WHERE community_id=?"
        db.execute(query, (data['name'], data['total_population'], data['elderly_population'], community_id))

    def delete_community(self, community_id):
        """删除社区 (仅限未关联老人的社区)"""
        check = db.execute("SELECT COUNT(*) FROM elderly WHERE community_id=?", (community_id,))
        if check[0][0] > 0:
            raise Exception("该社区已关联老人，无法删除")
        db.execute("DELETE FROM community WHERE community_id=?", (community_id,))

    # --- 老人管理 ---
    def add_elderly(self, data):
        """新增老人"""
        query = "INSERT INTO elderly (elderly_id, name, age, gender, community_id) VALUES (?, ?, ?, ?, ?)"
        db.execute(query, (data['elderly_id'], data['name'], data['age'], data['gender'], data['community_id']))

    def update_elderly(self, elderly_id, data):
        """更新老人信息"""
        query = "UPDATE elderly SET name=?, age=?, gender=?, community_id=? WHERE elderly_id=?"
        db.execute(query, (data['name'], data['age'], data['gender'], data['community_id'], elderly_id))

    def delete_elderly(self, elderly_id):
        """删除老人 (仅限无记录的老人)"""
        h_check = db.execute("SELECT COUNT(*) FROM health_record WHERE elderly_id=?", (elderly_id,))
        s_check = db.execute("SELECT COUNT(*) FROM service_record WHERE elderly_id=?", (elderly_id,))
        if h_check[0][0] > 0 or s_check[0][0] > 0:
            raise Exception("该老人已有健康或服务记录，无法删除")
        db.execute("DELETE FROM elderly WHERE elderly_id=?", (elderly_id,))

    # --- 护工管理 ---
    def get_caregivers(self, community_id=None):
        """获取护工列表"""
        query = "SELECT caregiver_id, name, community_id, qualification FROM caregiver"
        params = []
        if community_id:
            query += " WHERE community_id = ?"
            params.append(community_id)
        result = db.execute(query, params)
        return [{'caregiver_id': r[0], 'name': r[1], 'community_id': r[2], 'qualification': r[3]} for r in result]

    def add_caregiver(self, data):
        """新增护工"""
        query = "INSERT INTO caregiver (caregiver_id, name, community_id, qualification) VALUES (?, ?, ?, ?)"
        db.execute(query, (data['caregiver_id'], data['name'], data['community_id'], data['qualification']))

    # --- 排班管理 ---
    def get_schedules(self, caregiver_id=None, elderly_id=None):
        """获取排班列表"""
        query = "SELECT id, caregiver_id, elderly_id, service_type, service_date, service_time_slot, status FROM schedule"
        params = []
        conditions = []
        if caregiver_id:
            conditions.append("caregiver_id = ?")
            params.append(caregiver_id)
        if elderly_id:
            conditions.append("elderly_id = ?")
            params.append(elderly_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        result = db.execute(query, params)
        return [{
            'id': r[0], 'caregiver_id': r[1], 'elderly_id': r[2], 
            'service_type': r[3], 'service_date': r[4], 
            'service_time_slot': r[5], 'status': r[6]
        } for r in result]

    def add_schedule(self, data):
        """新增排班"""
        query = "INSERT INTO schedule (caregiver_id, elderly_id, service_type, service_date, service_time_slot) VALUES (?, ?, ?, ?, ?)"
        db.execute(query, (data['caregiver_id'], data['elderly_id'], data['service_type'], data['service_date'], data['service_time_slot']))

    # --- 健康记录管理 ---
    def add_health_record(self, data):
        """新增健康记录"""
        query = "INSERT INTO health_record (elderly_id, record_date, sbp, dbp, blood_sugar, heart_rate, health_status) VALUES (?, ?, ?, ?, ?, ?, ?)"
        db.execute(query, (data['elderly_id'], data['record_date'], data['sbp'], data['dbp'], data['blood_sugar'], data['heart_rate'], data['health_status']))

    # --- 服务记录管理 ---
    def add_service_record(self, data):
        """新增服务记录"""
        query = "INSERT INTO service_record (elderly_id, community_id, service_type, service_date, duration, satisfaction, caregiver_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
        db.execute(query, (data['elderly_id'], data['community_id'], data['service_type'], data['service_date'], data['duration'], data['satisfaction'], data['caregiver_id']))
    
    def get_seniors(self, page=1, page_size=20, community=''):
        """
        获取老人数据
        
        参数：
        - page: 页码
        - page_size: 每页大小
        - community: 社区筛选
        
        返回值：
        - dict: 老人数据和总数
        """
        # 构建查询：从 elderly 表分页查询基本信息，然后再补充健康状态和服务统计
        base_query = '''
        SELECT id, elderly_id, name, age, community_id FROM elderly
        '''

        if community:
            base_query += f" WHERE community_id = '{community}'"

        # 获取总数
        count_query = 'SELECT COUNT(*) FROM elderly'
        if community:
            count_query += f" WHERE community_id = '{community}'"
        total = db.execute(count_query)[0][0]

        # 获取分页数据
        offset = (page - 1) * page_size
        query = base_query + f" LIMIT {page_size} OFFSET {offset}"
        result = db.execute(query)

        # 处理结果
        items = []
        for row in result:
            # row: id, elderly_id, name, age, community_id
            e_id = row[1]

            # 获取老人的最新健康状态
            health_q = '''
            SELECT health_status FROM health_record WHERE elderly_id = ? ORDER BY record_date DESC LIMIT 1
            '''
            health_res = db.execute(health_q, (e_id,))
            health_status = health_res[0][0] if health_res else '未知'

            # 获取服务次数
            svc_q = 'SELECT COUNT(*) FROM service_record WHERE elderly_id = ?'
            svc_res = db.execute(svc_q, (e_id,))
            svc_count = svc_res[0][0] if svc_res else 0

            # 获取平均满意度
            sat_q = 'SELECT AVG(satisfaction) FROM service_record WHERE elderly_id = ?'
            sat_res = db.execute(sat_q, (e_id,))
            avg_sat = round(float(sat_res[0][0]), 1) if sat_res and sat_res[0][0] else 0

            items.append({
                'id': row[0],
                'elderly_id': row[1],
                'name': row[2],
                'age': row[3],
                'community_id': row[4],
                'health_status': health_status,
                'service_count': svc_count,
                'avg_satisfaction': avg_sat
            })
        
        return {
            'items': items,
            'total': total
        }
    
    def get_health_records(self, page=1, page_size=20, start_date='', end_date=''):
        """
        获取健康记录
        
        参数：
        - page: 页码
        - page_size: 每页大小
        - start_date: 开始日期
        - end_date: 结束日期
        
        返回值：
        - dict: 健康记录和总数
        """
        # 构建查询（健康记录使用 record_date 字段并使用 elderly_id）
        base_query = 'SELECT id, elderly_id, record_date, age, gender, community_id, health_status FROM health_record'

        where_clauses = []
        if start_date:
            where_clauses.append(f"record_date >= '{start_date}'")
        if end_date:
            where_clauses.append(f"record_date <= '{end_date}'")

        if where_clauses:
            base_query += ' WHERE ' + ' AND '.join(where_clauses)

        # 获取总数
        count_query = base_query.replace('SELECT id, elderly_id, record_date, age, gender, community_id, health_status', 'SELECT COUNT(*)')
        total = db.execute(count_query)[0][0]

        # 获取分页数据
        offset = (page - 1) * page_size
        query = base_query + f" ORDER BY record_date DESC LIMIT {page_size} OFFSET {offset}"
        result = db.execute(query)

        # 处理结果
        items = []
        for row in result:
            items.append({
                'id': row[0],
                'elderly_id': row[1],
                'record_date': row[2],
                'age': row[3],
                'gender': row[4],
                'community_id': row[5],
                'health_status': row[6]
            })
        
        return {
            'items': items,
            'total': total
        }
    
    def get_service_records(self, page=1, page_size=20, service_type=''):
        """
        获取服务记录
        
        参数：
        - page: 页码
        - page_size: 每页大小
        - service_type: 服务类型筛选
        
        返回值：
        - dict: 服务记录和总数
        """
        # 构建查询（服务记录使用 service_record 表）
        base_query = 'SELECT id, elderly_id, service_date, service_type, satisfaction, community_id FROM service_record'

        if service_type:
            base_query += f" WHERE service_type = '{service_type}'"

        # 获取总数
        count_query = base_query.replace('SELECT id, elderly_id, service_date, service_type, satisfaction, community_id', 'SELECT COUNT(*)')
        total = db.execute(count_query)[0][0]

        # 获取分页数据
        offset = (page - 1) * page_size
        query = base_query + f" ORDER BY service_date DESC LIMIT {page_size} OFFSET {offset}"
        result = db.execute(query)

        # 处理结果
        items = []
        for row in result:
            items.append({
                'id': row[0],
                'elderly_id': row[1],
                'service_date': row[2],
                'service_type': row[3],
                'satisfaction': row[4],
                'community_id': row[5]
            })
        
        return {
            'items': items,
            'total': total
        }
    
    def export_data(self):
        """
        导出数据
        
        返回值：
        - dict: 导出数据
        """
        # 获取老人数据
        seniors = db.execute('SELECT id, elderly_id, age, community_id FROM elderly')
        seniors_data = []
        for row in seniors:
            seniors_data.append({
                'id': row[0],
                'age': row[1],
                'community_id': row[2]
            })
        
        # 获取健康记录
        health_records = db.execute('SELECT id, elderly_id, record_date, age, gender, community_id, health_status FROM health_record')
        health_data = []
        for row in health_records:
            health_data.append({
                'id': row[0],
                'senior_id': row[1],
                'date': row[2],
                'sbp': row[3],
                'dbp': row[4],
                'blood_sugar': row[5],
                'heart_rate': row[6],
                'health_status': row[7]
            })
        
        # 获取服务记录
        service_records = db.execute('SELECT id, elderly_id, service_date, service_type, satisfaction, community_id FROM service_record')
        service_data = []
        for row in service_records:
            service_data.append({
                'id': row[0],
                'senior_id': row[1],
                'service_date': row[2],
                'service_type': row[3],
                'duration': row[4],
                'satisfaction': row[5],
                'community_id': row[6]
            })
        
        return {
            'seniors': seniors_data,
            'health_records': health_data,
            'service_records': service_data
        }
