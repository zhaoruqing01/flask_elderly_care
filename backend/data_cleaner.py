#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗模块

该模块用于清洗和预处理数据，包括：
1. 健康记录清洗（删除异常值、填充缺失值、统一日期格式）
2. 服务记录清洗（统一日期格式、调整满意度范围、过滤异常值）

使用说明：
- 运行 clean_all_data() 函数清洗所有数据
- 函数会返回清洗统计信息
"""

import sqlite3  # 用于操作 SQLite 数据库
import pandas as pd  # 用于数据处理
from datetime import datetime  # 用于处理日期

# 数据库文件路径
DB_PATH = 'database/elderly_care.db'


def clean_health_records():
    """
    清洗健康记录数据
    
    功能：
    1. 删除异常值（血压<0、心率>200）
    2. 按年龄段填充缺失的血糖值
    3. 统一日期格式
    4. 重新计算健康状态
    
    返回值：
    - 清洗统计信息，包含原始记录数、清洗后记录数、删除记录数、填充缺失值数
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        
        # 读取健康记录和老人信息
        health_df = pd.read_sql('SELECT * FROM health_record', conn)
        senior_df = pd.read_sql('SELECT id, age FROM senior', conn)
        
        # 检查数据是否为空
        if health_df.empty or senior_df.empty:
            conn.close()
            return {
                'original_count': 0,
                'cleaned_count': 0,
                'removed_count': 0,
                'filled_count': 0
            }
        
        # 合并数据，获取每个健康记录对应的老人年龄
        merged_df = pd.merge(health_df, senior_df, left_on='senior_id', right_on='id', suffixes=('', '_senior'))
        
        # 记录清洗前的记录数
        original_count = len(merged_df)
        
        # 1. 删除异常值：血压为负或心率 > 200 的记录
        cleaned_df = merged_df[(merged_df['sbp'] >= 0) & (merged_df['heart_rate'] <= 200)].copy()
        removed_count = original_count - len(cleaned_df)
        
        # 2. 按年龄段分组计算血糖均值
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
        cleaned_df['age_group'] = cleaned_df['age'].apply(get_age_group)
        
        # 计算每个年龄段的血糖均值
        age_group_means = cleaned_df.groupby('age_group')['blood_sugar'].mean()
        
        # 3. 填充缺失的血糖值
        def fill_blood_sugar(row):
            if pd.isna(row['blood_sugar']):  # 检查是否为缺失值
                age_group = get_age_group(row['age'])  # 获取年龄段
                # 使用对应年龄段的均值填充，若没有则使用整体均值
                return age_group_means.get(age_group, cleaned_df['blood_sugar'].mean())
            return row['blood_sugar']  # 非缺失值直接返回
        
        # 应用填充函数
        cleaned_df['blood_sugar'] = cleaned_df.apply(fill_blood_sugar, axis=1)
        
        # 4. 统一日期格式为 YYYY-MM-DD
        def normalize_date(date_str):
            try:
                # 尝试解析 YYYY-MM-DD 格式
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                return dt.strftime('%Y-%m-%d')
            except:
                try:
                    # 尝试解析 MM/DD/YYYY 格式
                    dt = datetime.strptime(date_str, '%m/%d/%Y')
                    return dt.strftime('%Y-%m-%d')
                except:
                    # 解析失败，返回当前日期
                    return datetime.now().strftime('%Y-%m-%d')
        
        # 应用日期标准化函数
        cleaned_df['date'] = cleaned_df['date'].apply(normalize_date)
        
        # 5. 重新计算健康状态
        def calculate_health_status(sbp, dbp, blood_sugar, heart_rate):
            if sbp >= 180 or dbp >= 110 or blood_sugar >= 11.1 or heart_rate > 140:
                return '高危'
            elif (sbp >= 140 or dbp >= 90) or (blood_sugar >= 7.0) or (heart_rate > 100):
                return '临界'
            else:
                return '良好'
        
        # 应用健康状态计算
        cleaned_df['health_status'] = cleaned_df.apply(
            lambda row: calculate_health_status(row['sbp'], row['dbp'], row['blood_sugar'], row['heart_rate']),
            axis=1
        )
        
        # 准备插入数据
        insert_data = cleaned_df[[
            'senior_id', 'date', 'sbp', 'dbp', 'blood_sugar', 'heart_rate', 'health_status'
        ]].values.tolist()
        
        # 清空原表并插入清洗后的数据
        cursor = conn.cursor()
        cursor.execute('DELETE FROM health_record')
        cursor.executemany(
            'INSERT INTO health_record (senior_id, date, sbp, dbp, blood_sugar, heart_rate, health_status) VALUES (?, ?, ?, ?, ?, ?, ?)',
            insert_data
        )
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        
        # 统计填充的缺失值数量
        filled_count = int(cleaned_df['blood_sugar'].isna().sum())
        
        # 返回清洗统计信息
        return {
            'original_count': original_count,
            'cleaned_count': len(cleaned_df),
            'removed_count': removed_count,
            'filled_count': filled_count
        }
    except Exception as e:
        # 发生错误时返回错误信息
        return {
            'original_count': 0,
            'cleaned_count': 0,
            'removed_count': 0,
            'filled_count': 0,
            'error': str(e)
        }


def clean_service_logs():
    """
    清洗服务记录数据
    
    功能：
    1. 统一日期格式
    2. 确保满意度在有效范围内（1-5）
    3. 确保服务时长为正数
    
    返回值：
    - 清洗统计信息，包含原始记录数、清洗后记录数、删除记录数
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        
        # 读取服务记录
        service_df = pd.read_sql('SELECT * FROM service_log', conn)
        
        # 检查数据是否为空
        if service_df.empty:
            conn.close()
            return {
                'original_count': 0,
                'cleaned_count': 0,
                'removed_count': 0
            }
        
        # 记录清洗前的记录数
        original_count = len(service_df)
        
        # 1. 统一日期格式
        def normalize_date(date_str):
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                return dt.strftime('%Y-%m-%d')
            except:
                # 解析失败，返回当前日期
                return datetime.now().strftime('%Y-%m-%d')
        
        # 应用日期标准化函数
        service_df['service_date'] = service_df['service_date'].apply(normalize_date)
        
        # 2. 确保满意度在有效范围内
        # 使用 lambda 函数将满意度限制在 1-5 之间
        service_df['satisfaction'] = service_df['satisfaction'].apply(lambda x: max(1, min(5, x)))
        
        # 3. 确保服务时长为正数
        service_df = service_df[service_df['duration'] > 0]
        
        # 计算清洗后的记录数和删除的记录数
        cleaned_count = len(service_df)
        removed_count = original_count - cleaned_count
        
        # 清空原表并插入清洗后的数据
        cursor = conn.cursor()
        cursor.execute('DELETE FROM service_log')
        insert_data = service_df[[
            'senior_id', 'service_date', 'service_type', 'duration', 'satisfaction', 'community_id'
        ]].values.tolist()
        cursor.executemany(
            'INSERT INTO service_log (senior_id, service_date, service_type, duration, satisfaction, community_id) VALUES (?, ?, ?, ?, ?, ?)',
            insert_data
        )
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        
        # 返回清洗统计信息
        return {
            'original_count': original_count,
            'cleaned_count': cleaned_count,
            'removed_count': removed_count
        }
    except Exception as e:
        # 发生错误时返回错误信息
        return {
            'original_count': 0,
            'cleaned_count': 0,
            'removed_count': 0,
            'error': str(e)
        }


def clean_all_data():
    """
    清洗所有数据
    
    功能：
    1. 清洗健康记录
    2. 清洗服务记录
    
    返回值：
    - 包含健康记录和服务记录清洗统计信息的字典
    """
    # 清洗健康记录
    health_stats = clean_health_records()
    # 清洗服务记录
    service_stats = clean_service_logs()
    
    # 返回综合结果
    return {
        'health': health_stats,
        'service': service_stats
    }


if __name__ == '__main__':
    """当直接运行此文件时，清洗所有数据并打印结果"""
    stats = clean_all_data()
    print("健康记录清洗结果:")
    print(f"原始记录数: {stats['health']['original_count']}")
    print(f"清洗后记录数: {stats['health']['cleaned_count']}")
    print(f"删除异常记录数: {stats['health']['removed_count']}")
    print(f"填充缺失值数: {stats['health']['filled_count']}")
    print("\n服务记录清洗结果:")
    print(f"原始记录数: {stats['service']['original_count']}")
    print(f"清洗后记录数: {stats['service']['cleaned_count']}")
    print(f"删除异常记录数: {stats['service']['removed_count']}")