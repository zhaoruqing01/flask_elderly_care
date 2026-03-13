"""健康服务模块

处理健康状态相关的业务逻辑
"""

import sqlite3
import pandas as pd
from app.utils.database import db

class HealthService:
    """健康服务类"""
    
    def get_health_distribution(self):
        """
        获取健康状态分布
        
        返回值：
        - dict: 健康状态分布数据
        """
        query = '''
        SELECT health_status, COUNT(*) as count 
        FROM health_record 
        GROUP BY health_status
        '''
        
        result = db.execute(query)
        
        # 定义健康状态顺序
        status_order = ['良好', '临界', '高危']
        counts = {status: 0 for status in status_order}
        
        # 填充数据
        for status, count in result:
            if status in counts:
                counts[status] = int(count)
        
        return {
            'values': [counts[status] for status in status_order]
        }
    
    def get_health_distribution_by_age(self):
        """
        按年龄段分析健康状态分布
        
        返回值：
        - dict: 按年龄段分析的健康状态分布数据
        """
        query = '''
        SELECT 
            CASE 
                WHEN s.age < 60 THEN '<60' 
                WHEN s.age >= 60 AND s.age < 70 THEN '60-69' 
                WHEN s.age >= 70 AND s.age < 80 THEN '70-79' 
                WHEN s.age >= 80 AND s.age < 90 THEN '80-89' 
                ELSE '90+' 
            END as age_group,
            h.health_status,
            COUNT(*) as count
        FROM health_record h
        JOIN senior s ON h.senior_id = s.id
        GROUP BY age_group, h.health_status
        ORDER BY age_group
        '''
        
        result = db.execute(query)
        
        # 处理结果
        age_groups = ['<60', '60-69', '70-79', '80-89', '90+']
        health_statuses = ['良好', '临界', '高危']
        
        data = {age: {status: 0 for status in health_statuses} for age in age_groups}
        
        for age_group, status, count in result:
            if age_group in data and status in data[age_group]:
                data[age_group][status] = int(count)
        
        # 转换为前端期望的格式
        datasets = []
        for status in health_statuses:
            dataset = {
                'name': status,
                'values': [data[age][status] for age in age_groups]
            }
            datasets.append(dataset)
        
        return {
            'age_groups': age_groups,
            'datasets': datasets
        }
    
    def get_health_trend(self):
        """
        获取健康状态趋势
        
        返回值：
        - dict: 健康状态趋势数据
        """
        query = '''
        SELECT 
            strftime('%Y-%m', date) as month,
            health_status,
            COUNT(*) as count
        FROM health_record
        GROUP BY month, health_status
        ORDER BY month
        '''
        
        result = db.execute(query)
        
        # 处理结果
        months = []
        health_statuses = ['良好', '临界', '高危']
        data = {status: [] for status in health_statuses}
        
        # 收集所有月份
        month_set = set()
        for month, _, _ in result:
            if month:
                month_set.add(month)
        months = sorted(month_set)
        
        # 重新查询获取完整数据
        result = db.execute(query)
        temp_data = {month: {status: 0 for status in health_statuses} for month in months}
        
        for month, status, count in result:
            if month in temp_data and status in temp_data[month]:
                temp_data[month][status] = int(count)
        
        # 构建返回数据
        for status in health_statuses:
            data[status] = [temp_data[month][status] for month in months]
        
        # 转换为前端期望的格式
        datasets = []
        for status in health_statuses:
            dataset = {
                'name': status,
                'values': data[status]
            }
            datasets.append(dataset)
        
        return {
            'dates': months,
            'datasets': datasets
        }
