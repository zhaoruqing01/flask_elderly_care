"""数据库初始化

创建数据库表结构并插入初始数据
"""

import sqlite3
import os
import sys

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# 数据库路径
db_path = app.config['DATABASE_PATH']

# 确保数据库目录存在
db_dir = os.path.dirname(db_path)
os.makedirs(db_dir, exist_ok=True)

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建老人表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seniors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER,
        community_id TEXT,
        health_status TEXT,
        service_count INTEGER,
        avg_satisfaction REAL
    )
    ''')
    
    # 创建健康记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        senior_id INTEGER,
        date TEXT,
        sbp INTEGER,
        dbp INTEGER,
        blood_sugar REAL,
        heart_rate INTEGER,
        health_status TEXT,
        FOREIGN KEY (senior_id) REFERENCES seniors (id)
    )
    ''')
    
    # 创建服务记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        senior_id INTEGER,
        service_date TEXT,
        service_type TEXT,
        duration INTEGER,
        satisfaction INTEGER,
        community_id TEXT,
        FOREIGN KEY (senior_id) REFERENCES seniors (id)
    )
    ''')
    
    # 插入初始数据
    # 插入老人数据
    seniors_data = [
        (65, '社区A', '良好', 5, 4.5),
        (72, '社区A', '临界', 8, 4.2),
        (68, '社区B', '良好', 3, 4.8),
        (75, '社区B', '高危', 10, 4.0),
        (70, '社区C', '良好', 4, 4.6),
        (69, '社区C', '临界', 6, 4.3),
        (71, '社区D', '良好', 2, 4.9),
        (73, '社区D', '高危', 9, 3.8),
        (67, '社区E', '良好', 3, 4.7),
        (74, '社区E', '临界', 7, 4.4)
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO seniors (age, community_id, health_status, service_count, avg_satisfaction)
    VALUES (?, ?, ?, ?, ?)
    ''', seniors_data)
    
    # 插入健康记录数据
    health_records_data = [
        (1, '2024-01-01', 120, 80, 5.6, 72, '良好'),
        (1, '2024-01-08', 118, 78, 5.5, 70, '良好'),
        (2, '2024-01-02', 130, 85, 6.1, 75, '临界'),
        (2, '2024-01-09', 132, 86, 6.2, 76, '临界'),
        (3, '2024-01-03', 115, 75, 5.4, 68, '良好'),
        (3, '2024-01-10', 116, 76, 5.3, 69, '良好'),
        (4, '2024-01-04', 145, 90, 7.2, 80, '高危'),
        (4, '2024-01-11', 148, 92, 7.3, 82, '高危'),
        (5, '2024-01-05', 118, 78, 5.5, 71, '良好'),
        (5, '2024-01-12', 119, 79, 5.6, 72, '良好')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO health_records (senior_id, date, sbp, dbp, blood_sugar, heart_rate, health_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', health_records_data)
    
    # 插入服务记录数据
    service_records_data = [
        (1, '2024-01-01', '助餐', 60, 5, '社区A'),
        (1, '2024-01-08', '助医', 45, 4, '社区A'),
        (2, '2024-01-02', '保洁', 90, 4, '社区A'),
        (2, '2024-01-09', '陪护', 120, 5, '社区A'),
        (3, '2024-01-03', '助餐', 60, 5, '社区B'),
        (3, '2024-01-10', '康复', 60, 5, '社区B'),
        (4, '2024-01-04', '助医', 45, 4, '社区B'),
        (4, '2024-01-11', '陪护', 120, 4, '社区B'),
        (5, '2024-01-05', '助餐', 60, 5, '社区C'),
        (5, '2024-01-12', '保洁', 90, 5, '社区C')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO service_records (senior_id, service_date, service_type, duration, satisfaction, community_id)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', service_records_data)
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("数据库初始化成功！")

if __name__ == '__main__':
    init_db()
