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
    def get_seniors(self, page=1, page_size=20, community=''):
        """获取老人数据分页"""
        base_query = 'SELECT id, elderly_id, name, age, community_id FROM elderly'
        params = []
        if community:
            base_query += " WHERE community_id = ?"
            params.append(community)

        # 获取总数
        count_query = 'SELECT COUNT(*) FROM elderly'
        if community:
            count_query += " WHERE community_id = ?"
        total = db.execute(count_query, params)[0][0]

        # 分页
        offset = (page - 1) * page_size
        query = base_query + " LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        result = db.execute(query, params)

        items = []
        for row in result:
            e_id = row[1]
            health_res = db.execute('SELECT health_status FROM health_record WHERE elderly_id = ? ORDER BY record_date DESC LIMIT 1', (e_id,))
            health_status = health_res[0][0] if health_res else '未知'
            svc_res = db.execute('SELECT COUNT(*) FROM service_record WHERE elderly_id = ?', (e_id,))
            svc_count = svc_res[0][0] if svc_res else 0
            sat_res = db.execute('SELECT AVG(satisfaction) FROM service_record WHERE elderly_id = ?', (e_id,))
            avg_sat = round(float(sat_res[0][0]), 1) if sat_res and sat_res[0][0] else 0

            items.append({
                'id': row[0], 'elderly_id': row[1], 'name': row[2], 'age': row[3],
                'community_id': row[4], 'health_status': health_status,
                'service_count': svc_count, 'avg_satisfaction': avg_sat
            })
        return {'items': items, 'total': total}

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
    def get_health_records(self, page=1, page_size=20, start_date='', end_date=''):
        """获取健康记录分页数据"""
        query = "SELECT elderly_id, record_date, sbp, dbp, blood_sugar, heart_rate, health_status FROM health_record"
        params = []
        conditions = []
        if start_date:
            conditions.append("record_date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("record_date <= ?")
            params.append(end_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        count_query = "SELECT COUNT(*) FROM health_record"
        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)
        total = db.execute(count_query, params)[0][0]

        offset = (page - 1) * page_size
        query += " ORDER BY record_date DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        
        result = db.execute(query, params)
        return {'items': [{
            'elderly_id': r[0], 'record_date': r[1], 'sbp': r[2], 
            'dbp': r[3], 'blood_sugar': r[4], 'heart_rate': r[5], 'health_status': r[6]
        } for r in result], 'total': total}

    def add_health_record(self, data):
        """新增健康记录"""
        query = "INSERT INTO health_record (elderly_id, record_date, sbp, dbp, blood_sugar, heart_rate, health_status) VALUES (?, ?, ?, ?, ?, ?, ?)"
        db.execute(query, (data['elderly_id'], data['record_date'], data['sbp'], data['dbp'], data['blood_sugar'], data['heart_rate'], data['health_status']))

    # --- 服务记录管理 ---
    def get_service_records(self, page=1, page_size=20, service_type=''):
        """获取服务记录分页数据"""
        query = "SELECT elderly_id, community_id, service_type, service_date, duration, satisfaction, caregiver_id FROM service_record"
        params = []
        if service_type:
            query += " WHERE service_type = ?"
            params.append(service_type)
        
        count_query = "SELECT COUNT(*) FROM service_record"
        if service_type:
            count_query += " WHERE service_type = ?"
        total = db.execute(count_query, params)[0][0]

        offset = (page - 1) * page_size
        query += " ORDER BY service_date DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        
        result = db.execute(query, params)
        return {'items': [{
            'elderly_id': r[0], 'community_id': r[1], 'service_type': r[2], 
            'service_date': r[3], 'duration': r[4], 'satisfaction': r[5], 'caregiver_id': r[6]
        } for r in result], 'total': total}

    def add_service_record(self, data):
        """新增服务记录"""
        query = "INSERT INTO service_record (elderly_id, community_id, service_type, service_date, duration, satisfaction, caregiver_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
        db.execute(query, (data['elderly_id'], data['community_id'], data['service_type'], data['service_date'], data['duration'], data['satisfaction'], data['caregiver_id']))

    # --- 预测结果管理 ---
    def get_predictions(self, community_id=None, service_type=None):
        """获取预测需求结果"""
        query = "SELECT community_id, service_type, prediction_date, predicted_demand FROM prediction_result"
        params = []
        conditions = []
        if community_id:
            conditions.append("community_id = ?")
            params.append(community_id)
        if service_type:
            conditions.append("service_type = ?")
            params.append(service_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        result = db.execute(query, params)
        return [{
            'community_id': r[0], 'service_type': r[1], 'prediction_date': r[2], 'predicted_demand': r[3]
        } for r in result]

    # --- 统计报表功能 ---
    def get_community_stats(self, community_id=None):
        """获取社区全景统计数据"""
        stats = {}
        pop_query = "SELECT community_id, name, total_population, elderly_population FROM community"
        if community_id:
            pop_query += " WHERE community_id = ?"
            pop_res = db.execute(pop_query, (community_id,))
        else:
            pop_res = db.execute(pop_query)
        
        stats['population'] = [{'community_id': r[0], 'name': r[1], 'total': r[2], 'elderly': r[3]} for r in pop_res]
        
        health_query = "SELECT e.community_id, hr.health_status, COUNT(*) FROM health_record hr JOIN elderly e ON hr.elderly_id = e.elderly_id GROUP BY e.community_id, hr.health_status"
        stats['health'] = db.execute(health_query)
        
        service_query = "SELECT community_id, service_type, COUNT(*), AVG(satisfaction) FROM service_record GROUP BY community_id, service_type"
        stats['service'] = db.execute(service_query)
        return stats

    def update_schedule_status(self, schedule_id, status):
        """更新排班/订单状态 (审核用)"""
        db.execute("UPDATE schedule SET status = ? WHERE id = ?", (status, schedule_id))
