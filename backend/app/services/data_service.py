"""数据服务模块

处理数据管理相关的业务逻辑
"""

import sqlite3
import pandas as pd
from app.utils.database import db

class DataService:
    """数据服务类"""
    
    def get_data_stats(self):
        """
        获取数据统计信息
        
        返回值：
        - dict: 数据统计信息
        """
        # 获取老人总数
        senior_count = db.execute('SELECT COUNT(*) FROM senior')[0][0]
        
        # 获取健康记录总数
        health_records = db.execute('SELECT COUNT(*) FROM health_record')[0][0]
        
        # 获取服务记录总数
        service_logs = db.execute('SELECT COUNT(*) FROM service_log')[0][0]
        
        # 获取社区数量
        communities = len(db.execute('SELECT DISTINCT community_id FROM senior'))
        
        return {
            'senior_count': senior_count,
            'health_records': health_records,
            'service_logs': service_logs,
            'communities': communities
        }
    
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
        # 构建查询
        base_query = '''
        SELECT 
            s.id, 
            s.age, 
            s.community_id,
            COALESCE((SELECT health_status FROM health_record WHERE senior_id = s.id ORDER BY date DESC LIMIT 1), '未知') as health_status,
            COALESCE((SELECT COUNT(*) FROM service_log WHERE senior_id = s.id), 0) as service_count,
            COALESCE((SELECT AVG(satisfaction) FROM service_log WHERE senior_id = s.id), 0) as avg_satisfaction
        FROM senior s
        '''
        
        if community:
            base_query += f" WHERE s.community_id = '{community}'"
        
        # 获取总数
        count_query = base_query.replace('SELECT s.id, s.age, s.community_id, COALESCE((SELECT health_status FROM health_record WHERE senior_id = s.id ORDER BY date DESC LIMIT 1), '未知') as health_status, COALESCE((SELECT COUNT(*) FROM service_log WHERE senior_id = s.id), 0) as service_count, COALESCE((SELECT AVG(satisfaction) FROM service_log WHERE senior_id = s.id), 0) as avg_satisfaction', 'SELECT COUNT(*)')
        total = db.execute(count_query)[0][0]
        
        # 获取分页数据
        offset = (page - 1) * page_size
        query = base_query + f" LIMIT {page_size} OFFSET {offset}"
        result = db.execute(query)
        
        # 处理结果
        items = []
        for row in result:
            items.append({
                'id': row[0],
                'age': row[1],
                'community_id': row[2],
                'health_status': row[3],
                'service_count': row[4],
                'avg_satisfaction': round(row[5], 1) if row[5] else 0
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
        # 构建查询
        base_query = 'SELECT id, senior_id, date, sbp, dbp, blood_sugar, heart_rate, health_status FROM health_record'
        
        where_clauses = []
        if start_date:
            where_clauses.append(f"date >= '{start_date}'")
        if end_date:
            where_clauses.append(f"date <= '{end_date}'")
        
        if where_clauses:
            base_query += ' WHERE ' + ' AND '.join(where_clauses)
        
        # 获取总数
        count_query = base_query.replace('SELECT id, senior_id, date, sbp, dbp, blood_sugar, heart_rate, health_status', 'SELECT COUNT(*)')
        total = db.execute(count_query)[0][0]
        
        # 获取分页数据
        offset = (page - 1) * page_size
        query = base_query + f" ORDER BY date DESC LIMIT {page_size} OFFSET {offset}"
        result = db.execute(query)
        
        # 处理结果
        items = []
        for row in result:
            items.append({
                'id': row[0],
                'senior_id': row[1],
                'date': row[2],
                'sbp': row[3],
                'dbp': row[4],
                'blood_sugar': row[5],
                'heart_rate': row[6],
                'health_status': row[7]
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
        # 构建查询
        base_query = 'SELECT id, senior_id, service_date, service_type, duration, satisfaction, community_id FROM service_log'
        
        if service_type:
            base_query += f" WHERE service_type = '{service_type}'"
        
        # 获取总数
        count_query = base_query.replace('SELECT id, senior_id, service_date, service_type, duration, satisfaction, community_id', 'SELECT COUNT(*)')
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
                'senior_id': row[1],
                'service_date': row[2],
                'service_type': row[3],
                'duration': row[4],
                'satisfaction': row[5],
                'community_id': row[6]
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
        seniors = db.execute('SELECT id, age, community_id FROM senior')
        seniors_data = []
        for row in seniors:
            seniors_data.append({
                'id': row[0],
                'age': row[1],
                'community_id': row[2]
            })
        
        # 获取健康记录
        health_records = db.execute('SELECT id, senior_id, date, sbp, dbp, blood_sugar, heart_rate, health_status FROM health_record')
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
        service_records = db.execute('SELECT id, senior_id, service_date, service_type, duration, satisfaction, community_id FROM service_log')
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
