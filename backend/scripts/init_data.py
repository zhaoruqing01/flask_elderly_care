"""数据初始化脚本

初始化数据库和基础数据
"""

import os
import sys
import sqlite3

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_generator import generate_and_insert

def init_database():
    """
    初始化数据库
    """
    # 数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database', 'elderly_care.db')
    
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
    create_tables(cursor)
    
    # 提交并关闭连接
    conn.commit()
    conn.close()
    
    print("数据库初始化完成！")

def create_tables(cursor):
    """
    创建数据库表
    
    参数：
    - cursor: 数据库游标
    """
    # 创建健康记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elderly_id TEXT,
        age INTEGER,
        gender TEXT,
        community_id TEXT,
        health_status TEXT,
        record_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建服务记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elderly_id TEXT,
        community_id TEXT,
        service_type TEXT,
        service_date DATE,
        satisfaction INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建社区表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS community (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        community_id TEXT UNIQUE,
        name TEXT,
        population INTEGER,
        elderly_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建老年人表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS elderly (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elderly_id TEXT UNIQUE,
        name TEXT,
        age INTEGER,
        gender TEXT,
        community_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

def init_sample_data():
    """
    初始化样例数据
    """
    print("开始生成样例数据...")
    generate_and_insert()
    print("样例数据生成完成！")

if __name__ == '__main__':
    """脚本入口"""
    init_database()
    init_sample_data()
