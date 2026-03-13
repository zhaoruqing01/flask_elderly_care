#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据生成器模块

该模块用于生成模拟的老年人健康数据和服务使用数据
包括：
1. 老人基本信息
2. 健康记录（血压、血糖、心率等）
3. 服务使用记录（助餐、助医、保洁等）

使用说明：
- 运行 generate_and_insert() 函数生成所有数据
- 数据会自动存储到 SQLite 数据库
"""

import sqlite3  # 用于操作 SQLite 数据库
import random   # 用于生成随机数
from faker import Faker  # 用于生成模拟数据
from datetime import datetime, timedelta  # 用于处理日期
import os  # 用于操作文件系统

# 初始化 Faker 实例，使用中文
fake = Faker('zh_CN')

# 数据库文件路径
import os
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'database', 'elderly_care.db')

# 服务类型列表
SERVICE_TYPES = ['助餐', '助医', '保洁', '陪护', '康复']

# 社区列表
COMMUNITIES = ['社区A', '社区B', '社区C', '社区D', '社区E']


def init_database():
    """
    初始化数据库，创建表结构
    
    功能：
    1. 自动创建数据库目录
    2. 连接到 SQLite 数据库
    3. 创建四个数据表：
       - senior：老人基本信息表
       - health_record：健康记录表
       - service_log：服务使用记录表
       - prediction_result：预测结果表
    """
    # 创建数据库目录（如果不存在）
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建老人基本信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS senior (
        id INTEGER PRIMARY KEY,  -- 老人ID，主键
        age INTEGER,  -- 年龄
        community_id TEXT  -- 社区ID
    )
    ''')
    
    # 创建健康监测表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_record (
        id INTEGER PRIMARY KEY,  -- 记录ID，主键
        senior_id INTEGER,  -- 老人ID，外键
        date TEXT,  -- 记录日期
        sbp INTEGER,  -- 收缩压
        dbp INTEGER,  -- 舒张压
        blood_sugar REAL,  -- 血糖
        heart_rate INTEGER,  -- 心率
        health_status TEXT,  -- 健康状态（良好/临界/高危）
        FOREIGN KEY (senior_id) REFERENCES senior (id)  -- 外键约束
    )
    ''')
    
    # 创建服务使用记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_log (
        id INTEGER PRIMARY KEY,  -- 记录ID，主键
        senior_id INTEGER,  -- 老人ID，外键
        service_date TEXT,  -- 服务日期
        service_type TEXT,  -- 服务类型
        duration INTEGER,  -- 服务时长（分钟）
        satisfaction INTEGER,  -- 满意度（1-5）
        community_id TEXT,  -- 社区ID
        FOREIGN KEY (senior_id) REFERENCES senior (id)  -- 外键约束
    )
    ''')
    
    # 创建预测结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prediction_result (
        id INTEGER PRIMARY KEY,  -- 记录ID，主键
        community_id TEXT,  -- 社区ID
        service_type TEXT,  -- 服务类型
        predict_date TEXT,  -- 预测日期
        predicted_demand REAL  -- 预测需求量
    )
    ''')
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()


def calculate_health_status(sbp, dbp, blood_sugar, heart_rate):
    """
    根据健康指标计算健康状态
    
    参数：
    - sbp: 收缩压
    - dbp: 舒张压
    - blood_sugar: 血糖
    - heart_rate: 心率
    
    返回值：
    - 健康状态：'高危'、'临界' 或 '良好'
    """
    # 高危判断：血压极高、血糖极高或心率过快
    if sbp >= 180 or dbp >= 110 or blood_sugar >= 11.1 or heart_rate > 140:
        return '高危'
    # 临界判断：血压偏高、血糖偏高或心率偏快
    elif (sbp >= 140 or dbp >= 90) or (blood_sugar >= 7.0) or (heart_rate > 100):
        return '临界'
    # 良好判断：各项指标正常
    else:
        return '良好'


def generate_senior_data():
    """
    生成老人基本信息数据
    
    返回值：
    - 老人信息列表，每个元素是一个元组 (id, age, community_id)
    """
    seniors = []
    # 生成300位老人
    for i in range(1, 301):
        age = random.randint(60, 90)  # 年龄在60-90岁之间
        community_id = random.choice(COMMUNITIES)  # 随机分配到一个社区
        seniors.append((i, age, community_id))
    return seniors


def generate_health_records(senior_id, age):
    """
    为指定老人生成健康记录
    
    参数：
    - senior_id: 老人ID
    - age: 老人年龄
    
    返回值：
    - 健康记录列表，每个元素包含老人ID、日期、血压、血糖、心率、健康状态
    """
    records = []
    end_date = datetime.now()  # 结束日期：当前时间
    start_date = end_date - timedelta(days=180)  # 开始日期：6个月前
    
    # 随机设置健康风险等级
    # 0: 健康（60%概率）
    # 1: 临界（30%概率）
    # 2: 高危（10%概率）
    health_risk_level = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
    
    current_date = start_date
    while current_date <= end_date:
        # 30%的概率生成记录（每月约2-4条）
        if random.random() < 0.3:
            # 根据年龄和健康风险等级计算基础健康指标
            base_sbp = 120 + (age - 60) * 0.5 + health_risk_level * 25  # 基础收缩压
            base_dbp = 80 + (age - 60) * 0.3 + health_risk_level * 15  # 基础舒张压
            base_sugar = 5.6 + (age - 60) * 0.02 + health_risk_level * 2  # 基础血糖
            base_heart_rate = 75 + (age - 60) * 0.2 + health_risk_level * 10  # 基础心率
            
            # 添加随机波动
            sbp = int(base_sbp + random.uniform(-10, 20))
            dbp = int(base_dbp + random.uniform(-8, 15))
            blood_sugar = round(base_sugar + random.uniform(-0.5, 2), 1)
            heart_rate = int(base_heart_rate + random.uniform(-10, 20))
            
            # 生成异常值（3%的概率）
            if random.random() < 0.03:
                sbp = random.choice([-10, -5, 0])  # 异常低的血压
            if random.random() < 0.03:
                heart_rate = random.randint(201, 250)  # 异常高的心率
            if random.random() < 0.08:
                blood_sugar = None  # 缺失的血糖值
            if random.random() < 0.05:
                date_str = current_date.strftime('%m/%d/%Y')  # 错误的日期格式
            else:
                date_str = current_date.strftime('%Y-%m-%d')  # 正确的日期格式
            
            # 计算健康状态
            health_status = calculate_health_status(sbp, dbp, blood_sugar or 0, heart_rate)
            # 添加记录
            records.append((senior_id, date_str, sbp, dbp, blood_sugar, heart_rate, health_status))
        current_date += timedelta(days=1)  # 日期加1天
    return records

# 服务基础需求量配置
SERVICE_BASE_DEMAND = {
    '助餐': {'base': 120, 'variance': 30},  # 基础需求120，波动30
    '助医': {'base': 80, 'variance': 25},   # 基础需求80，波动25
    '保洁': {'base': 100, 'variance': 20},  # 基础需求100，波动20
    '陪护': {'base': 90, 'variance': 35},   # 基础需求90，波动35
    '康复': {'base': 60, 'variance': 20}    # 基础需求60，波动20
}

# 社区服务偏好配置
COMMUNITY_SERVICE_PREFERENCE = {
    '社区A': {'助餐': 1.2, '助医': 0.9, '保洁': 1.1, '陪护': 0.8, '康复': 1.0},  # 社区A偏好助餐
    '社区B': {'助餐': 0.9, '助医': 1.1, '保洁': 1.0, '陪护': 1.2, '康复': 0.8},  # 社区B偏好陪护
    '社区C': {'助餐': 1.0, '助医': 1.0, '保洁': 0.9, '陪护': 1.0, '康复': 1.1},  # 社区C偏好康复
    '社区D': {'助餐': 1.1, '助医': 0.8, '保洁': 1.2, '陪护': 0.9, '康复': 1.0},  # 社区D偏好保洁
    '社区E': {'助餐': 0.8, '助医': 1.2, '保洁': 1.0, '陪护': 1.1, '康复': 1.2}   # 社区E偏好助医和康复
}


def generate_service_logs(senior_id, community_id, age):
    """
    为指定老人生成服务使用记录
    
    参数：
    - senior_id: 老人ID
    - community_id: 社区ID
    - age: 老人年龄
    
    返回值：
    - 服务记录列表，每个元素包含老人ID、服务日期、服务类型、时长、满意度、社区ID
    """
    logs = []
    end_date = datetime.now()  # 结束日期：当前时间
    start_date = end_date - timedelta(days=365)  # 开始日期：1年前
    
    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday()  # 获取星期几（0-6，0是周一）
        is_weekend = day_of_week >= 5  # 判断是否周末
        month = current_date.month  # 获取月份
        
        # 季节性因素
        season_factor = 1.0
        if month in [12, 1, 2]:  # 冬季
            season_factor = 1.3  # 需求增加30%
        elif month in [6, 7, 8]:  # 夏季
            season_factor = 0.85  # 需求减少15%
        
        # 周末因素
        weekend_factor = 1.15 if is_weekend else 1.0  # 周末需求增加15%
        
        # 遍历每种服务类型
        for service_type in SERVICE_TYPES:
            base_demand = SERVICE_BASE_DEMAND[service_type]['base']  # 基础需求量
            variance = SERVICE_BASE_DEMAND[service_type]['variance']  # 波动范围
            community_pref = COMMUNITY_SERVICE_PREFERENCE[community_id][service_type]  # 社区偏好
            
            # 计算预期需求量
            expected_demand = base_demand * community_pref * season_factor * weekend_factor
            # 计算生成记录的概率（最大25%）
            prob = min(0.25, expected_demand / 1000)
            
            # 根据概率生成记录
            if random.random() < prob:
                # 生成服务时长
                duration = int(expected_demand + random.gauss(0, variance))
                duration = max(30, min(240, duration))  # 限制在30-240分钟之间
                # 生成满意度（加权随机）
                # 1分(5%)、2分(10%)、3分(20%)、4分(35%)、5分(30%)
                satisfaction = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
                # 添加记录
                logs.append((senior_id, current_date.strftime('%Y-%m-%d'), service_type, duration, satisfaction, community_id))
        
        current_date += timedelta(days=1)  # 日期加1天
    return logs


def generate_and_insert():
    """
    生成所有模拟数据并插入数据库
    
    流程：
    1. 初始化数据库
    2. 清空现有数据
    3. 生成老人数据并插入
    4. 为每位老人生成健康记录和服务记录并插入
    
    返回值：
    - True：生成成功
    """
    # 初始化数据库
    init_database()
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute('DELETE FROM service_log')
    cursor.execute('DELETE FROM health_record')
    cursor.execute('DELETE FROM senior')
    cursor.execute('DELETE FROM prediction_result')
    conn.commit()
    
    # 生成老人数据
    seniors = generate_senior_data()
    # 批量插入老人数据
    cursor.executemany('INSERT INTO senior VALUES (?, ?, ?)', seniors)
    conn.commit()
    
    # 为每位老人生成健康记录和服务记录
    for senior in seniors:
        senior_id = senior[0]
        age = senior[1]
        community_id = senior[2]
        
        # 生成健康记录
        health_records = generate_health_records(senior_id, age)
        if health_records:
            # 批量插入健康记录
            cursor.executemany('INSERT INTO health_record (senior_id, date, sbp, dbp, blood_sugar, heart_rate, health_status) VALUES (?, ?, ?, ?, ?, ?, ?)', health_records)
        
        # 生成服务记录
        service_logs = generate_service_logs(senior_id, community_id, age)
        if service_logs:
            # 批量插入服务记录
            cursor.executemany('INSERT INTO service_log (senior_id, service_date, service_type, duration, satisfaction, community_id) VALUES (?, ?, ?, ?, ?, ?)', service_logs)
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    return True


if __name__ == '__main__':
    """当直接运行此文件时，生成数据"""
    generate_and_insert()
    print("模拟数据生成完成！")