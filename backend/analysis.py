#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析模块

该模块用于分析数据并生成统计结果，包括：
1. 健康状态分析（分布、按年龄分析、趋势）
2. 服务使用分析（频次、按社区分析、满意度、趋势）
3. 关键指标计算（老人总数、服务总数、平均满意度、高危人数）

使用说明：
- 直接调用相应函数获取分析结果
- 函数会返回格式化的数据，可直接用于前端展示
"""

import sqlite3  # 用于操作 SQLite 数据库
import pandas as pd  # 用于数据处理
from datetime import datetime, timedelta  # 用于处理日期

# 数据库文件路径
import os
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'database', 'elderly_care.db')


def get_health_distribution():
    """
    获取健康状态分布数据
    
    功能：
    - 统计每个老人的最新健康状态
    - 计算良好、临界、高危的老人数量
    
    返回值：
    - 包含健康状态类别和对应数量的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        # SQL查询：获取每个老人的最新健康记录
        query = '''
        SELECT senior_id, health_status
        FROM (
            SELECT senior_id, health_status, date,
                   ROW_NUMBER() OVER (PARTITION BY senior_id ORDER BY date DESC) as rn
            FROM health_record
        ) t
        WHERE rn = 1
        '''
        health_df = pd.read_sql(query, conn)
        conn.close()
        
        # 统计各健康状态的老人数量
        distribution = health_df['health_status'].value_counts().to_dict()
    except:
        # 发生错误时返回空字典
        distribution = {}
    
    # 确保所有状态都有值
    statuses = ['良好', '临界', '高危']
    for status in statuses:
        if status not in distribution:
            distribution[status] = 0
    
    # 返回结果
    return {
        'categories': statuses,
        'values': [distribution[status] for status in statuses]
    }


def get_health_distribution_by_age():
    """
    按年龄段分析健康状态分布
    
    功能：
    - 统计每个年龄段（60-69、70-79、80-89、90+）的健康状态分布
    
    返回值：
    - 包含年龄段和各健康状态数据的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        # 获取每个老人的最新健康记录
        health_query = '''
        SELECT senior_id, health_status
        FROM (
            SELECT senior_id, health_status, date,
                   ROW_NUMBER() OVER (PARTITION BY senior_id ORDER BY date DESC) as rn
            FROM health_record
        ) t
        WHERE rn = 1
        '''
        health_df = pd.read_sql(health_query, conn)
        # 获取老人年龄信息
        senior_df = pd.read_sql('SELECT id, age FROM senior', conn)
        conn.close()
        
        # 合并健康记录和老人信息
        merged_df = pd.merge(health_df, senior_df, left_on='senior_id', right_on='id')
        
        # 定义年龄段划分函数
        def get_age_group(age):
            if age < 70:
                return '60-69'
            elif age < 80:
                return '70-79'
            elif age < 90:
                return '80-89'
            else:
                return '90+'
        
        # 为每条记录添加年龄段
        merged_df['age_group'] = merged_df['age'].apply(get_age_group)
        # 按年龄段和健康状态分组统计
        grouped = merged_df.groupby(['age_group', 'health_status']).size().unstack(fill_value=0)
        
        # 确保所有状态都有列
        statuses = ['良好', '临界', '高危']
        for status in statuses:
            if status not in grouped.columns:
                grouped[status] = 0
        
        # 构建结果
        result = {
            'age_groups': list(grouped.index),
            'datasets': []
        }
        
        # 为每种健康状态添加数据
        for status in statuses:
            series_data = grouped[status]
            data_list = series_data.tolist()
            result['datasets'].append({
                'name': status,
                'data': data_list
            })
        
        return result
    except:
        # 发生错误时返回空数据
        return {
            'age_groups': ['60-69', '70-79', '80-89', '90+'],
            'datasets': [
                {'name': '良好', 'data': [0, 0, 0, 0]},
                {'name': '临界', 'data': [0, 0, 0, 0]},
                {'name': '高危', 'data': [0, 0, 0, 0]}
            ]
        }


def get_service_frequency():
    """
    获取服务使用频次数据
    
    功能：
    - 统计每种服务类型的使用次数
    
    返回值：
    - 包含服务类型和对应使用次数的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        # 读取服务记录
        service_df = pd.read_sql('SELECT service_type FROM service_log', conn)
        conn.close()
        
        # 统计各服务类型的使用次数
        frequency = service_df['service_type'].value_counts().to_dict()
    except:
        # 发生错误时返回空字典
        frequency = {}
    
    # 服务类型列表
    service_types = ['助餐', '助医', '保洁', '陪护', '康复']
    
    # 返回结果
    return {
        'types': service_types,
        'counts': [frequency.get(service, 0) for service in service_types]
    }


def get_service_frequency_by_community():
    """
    按社区分析服务使用频次
    
    功能：
    - 统计每个社区每种服务类型的使用次数
    
    返回值：
    - 包含社区和各服务类型使用次数的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        # 读取服务记录
        service_df = pd.read_sql('SELECT community_id, service_type FROM service_log', conn)
        conn.close()
        
        # 按社区和服务类型分组统计
        grouped = service_df.groupby(['community_id', 'service_type']).size().unstack(fill_value=0)
        
        # 服务类型列表
        service_types = ['助餐', '助医', '保洁', '陪护', '康复']
        
        # 确保所有服务类型都有列
        for service in service_types:
            if service not in grouped.columns:
                grouped[service] = 0
        
        # 构建结果
        result = {
            'communities': list(grouped.index),
            'datasets': []
        }
        
        # 为每种服务类型添加数据
        for service in service_types:
            series_data = grouped[service]
            data_list = series_data.tolist()
            result['datasets'].append({
                'name': service,
                'data': data_list
            })
        
        return result
    except:
        # 发生错误时返回空数据
        return {
            'communities': ['社区A', '社区B', '社区C', '社区D'],
            'datasets': [
                {'name': '助餐', 'data': [0, 0, 0, 0]},
                {'name': '助医', 'data': [0, 0, 0, 0]},
                {'name': '保洁', 'data': [0, 0, 0, 0]},
                {'name': '陪护', 'data': [0, 0, 0, 0]},
                {'name': '康复', 'data': [0, 0, 0, 0]}
            ]
        }


def get_service_satisfaction():
    """
    获取服务满意度数据
    
    功能：
    - 计算每种服务类型的平均满意度
    
    返回值：
    - 包含服务类型和对应平均满意度的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        # 读取服务记录
        service_df = pd.read_sql('SELECT service_type, satisfaction FROM service_log', conn)
        conn.close()
        
        # 按服务类型计算平均满意度
        satisfaction = service_df.groupby('service_type')['satisfaction'].mean().to_dict()
    except:
        # 发生错误时返回空字典
        satisfaction = {}
    
    # 服务类型列表
    service_types = ['助餐', '助医', '保洁', '陪护', '康复']
    
    # 返回结果，保留一位小数
    return {
        'types': service_types,
        'satisfaction': [round(satisfaction.get(service, 0), 1) for service in service_types]
    }


def get_key_indicators():
    """
    获取关键指标数据
    
    功能：
    - 计算老人总数
    - 计算服务总数
    - 计算平均满意度
    - 计算高危老人数量
    
    返回值：
    - 包含所有关键指标的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        
        # 计算老人总数
        senior_count = pd.read_sql('SELECT COUNT(*) as count FROM senior', conn).iloc[0]['count']
        
        # 计算服务总数
        service_count = pd.read_sql('SELECT COUNT(*) as count FROM service_log', conn).iloc[0]['count']
        
        # 计算平均满意度
        avg_satisfaction = pd.read_sql('SELECT AVG(satisfaction) as avg FROM service_log', conn).iloc[0]['avg']
        avg_satisfaction = round(avg_satisfaction, 1) if pd.notna(avg_satisfaction) else 0
        
        # 计算高危老人数量
        high_risk_query = '''
        SELECT COUNT(*) as count
        FROM (
            SELECT senior_id, health_status,
                   ROW_NUMBER() OVER (PARTITION BY senior_id ORDER BY date DESC) as rn
            FROM health_record
        ) t
        WHERE rn = 1 AND health_status = '高危'
        '''
        high_risk_count = pd.read_sql(high_risk_query, conn).iloc[0]['count']
        
        conn.close()
    except:
        # 发生错误时返回默认值
        return {
            'senior_count': 0,
            'service_count': 0,
            'avg_satisfaction': 0,
            'high_risk_count': 0
        }
    
    # 返回结果，确保所有数据类型都是Python原生类型
    return {
        'senior_count': int(senior_count),
        'service_count': int(service_count),
        'avg_satisfaction': float(avg_satisfaction),
        'high_risk_count': int(high_risk_count)
    }


def get_health_trend():
    """
    获取健康状态趋势数据（过去30天）
    
    功能：
    - 统计过去30天每天的健康状态分布
    
    返回值：
    - 包含日期和各健康状态数据的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # SQL查询：统计每天各健康状态的记录数
        query = f'''
        SELECT date, health_status, COUNT(*) as count
        FROM health_record
        WHERE date >= '{start_date.strftime('%Y-%m-%d')}'
        GROUP BY date, health_status
        ORDER BY date
        '''
        trend_df = pd.read_sql(query, conn)
        conn.close()
        
        # 获取所有日期
        dates = sorted(trend_df['date'].unique().tolist())
        # 健康状态列表
        statuses = ['良好', '临界', '高危']
        
        # 构建结果
        result = {
            'dates': dates,
            'datasets': []
        }
        
        # 为每种健康状态添加数据
        for status in statuses:
            status_data = trend_df[trend_df['health_status'] == status]
            data_dict = dict(zip(status_data['date'], status_data['count']))
            # 确保每个日期都有数据
            data_list = [data_dict.get(date, 0) for date in dates]
            result['datasets'].append({
                'name': status,
                'data': data_list
            })
        
        return result
    except:
        # 发生错误时返回空数据
        return {
            'dates': [],
            'datasets': [
                {'name': '良好', 'data': []},
                {'name': '临界', 'data': []},
                {'name': '高危', 'data': []}
            ]
        }


def get_service_trend():
    """
    获取服务使用趋势数据（过去30天）
    
    功能：
    - 统计过去30天每天的服务使用情况
    
    返回值：
    - 包含日期和各服务类型使用次数的字典
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # SQL查询：统计每天各服务类型的使用次数
        query = f'''
        SELECT date, service_type, COUNT(*) as count
        FROM service_log
        WHERE date >= '{start_date.strftime('%Y-%m-%d')}'
        GROUP BY date, service_type
        ORDER BY date
        '''
        trend_df = pd.read_sql(query, conn)
        conn.close()
        
        # 获取所有日期
        dates = sorted(trend_df['date'].unique().tolist())
        # 服务类型列表
        service_types = ['助餐', '助医', '保洁', '陪护', '康复']
        
        # 构建结果
        result = {
            'dates': dates,
            'datasets': []
        }
        
        # 为每种服务类型添加数据
        for service in service_types:
            service_data = trend_df[trend_df['service_type'] == service]
            data_dict = dict(zip(service_data['date'], service_data['count']))
            # 确保每个日期都有数据
            data_list = [data_dict.get(date, 0) for date in dates]
            result['datasets'].append({
                'name': service,
                'data': data_list
            })
        
        return result
    except:
        # 发生错误时返回空数据
        return {
            'dates': [],
            'datasets': [
                {'name': '助餐', 'data': []},
                {'name': '助医', 'data': []},
                {'name': '保洁', 'data': []},
                {'name': '陪护', 'data': []},
                {'name': '康复', 'data': []}
            ]
        }