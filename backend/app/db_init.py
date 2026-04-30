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
    
    # 删除旧表以重建新结构
    tables_to_drop = ['users', 'community', 'elderly', 'caregiver', 'schedule', 'health_record', 'service_record', 'prediction_result']
    for table in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # 1. 用户表 (RBAC)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT, -- 'institution', 'caregiver', 'regulatory'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. 社区表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS community (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        community_id TEXT UNIQUE,
        name TEXT,
        total_population INTEGER,
        elderly_population INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. 老人表 (elderly)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS elderly (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elderly_id TEXT UNIQUE,
        name TEXT,
        age INTEGER,
        gender TEXT,
        community_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (community_id) REFERENCES community (community_id)
    )
    ''')
    
    # 4. 护工表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS caregiver (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caregiver_id TEXT UNIQUE,
        name TEXT,
        community_id TEXT,
        qualification TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (community_id) REFERENCES community (community_id)
    )
    ''')

    # 5. 护工排班表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caregiver_id TEXT,
        elderly_id TEXT,
        service_type TEXT,
        service_date TEXT,
        service_time_slot TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (caregiver_id) REFERENCES caregiver (caregiver_id),
        FOREIGN KEY (elderly_id) REFERENCES elderly (elderly_id)
    )
    ''')

    # 6. 健康记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elderly_id TEXT,
        record_date TEXT,
        sbp INTEGER,
        dbp INTEGER,
        blood_sugar REAL,
        heart_rate INTEGER,
        health_status TEXT,
        FOREIGN KEY (elderly_id) REFERENCES elderly (elderly_id)
    )
    ''')
    
    # 7. 服务记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elderly_id TEXT,
        community_id TEXT,
        service_type TEXT,
        service_date TEXT,
        duration INTEGER,
        satisfaction INTEGER,
        caregiver_id TEXT,
        FOREIGN KEY (elderly_id) REFERENCES elderly (elderly_id),
        FOREIGN KEY (community_id) REFERENCES community (community_id),
        FOREIGN KEY (caregiver_id) REFERENCES caregiver (caregiver_id)
    )
    ''')

    # 8. 预测结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prediction_result (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        community_id TEXT,
        service_type TEXT,
        prediction_date TEXT,
        predicted_demand REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (community_id) REFERENCES community (community_id)
    )
    ''')

    # 兼容旧表 seniors 和 health_records, service_records
    cursor.execute('CREATE TABLE IF NOT EXISTS seniors (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, community_id TEXT, health_status TEXT, service_count INTEGER, avg_satisfaction REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS health_records (id INTEGER PRIMARY KEY AUTOINCREMENT, senior_id INTEGER, date TEXT, sbp INTEGER, dbp INTEGER, blood_sugar REAL, heart_rate INTEGER, health_status TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS service_records (id INTEGER PRIMARY KEY AUTOINCREMENT, senior_id INTEGER, service_date TEXT, service_type TEXT, duration INTEGER, satisfaction INTEGER, community_id TEXT)')

    # 插入默认用户
    users_data = [
        ('admin', '123456', 'institution'),
        ('caregiver1', '123456', 'caregiver'),
        ('gov', '123456', 'regulatory')
    ]
    cursor.executemany('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', users_data)

    # 插入初始社区数据
    communities_data = [
        ('C001', '社区A', 5000, 800),
        ('C002', '社区B', 4500, 750),
        ('C003', '社区C', 6000, 1000),
        ('C004', '社区D', 4000, 600),
        ('C005', '社区E', 5500, 900)
    ]
    cursor.executemany('INSERT OR IGNORE INTO community (community_id, name, total_population, elderly_population) VALUES (?, ?, ?, ?)', communities_data)
    
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

    # 也插入到兼容的 health_record 表（将 senior_id -> elderly_id 假设一一对应）
    for rec in health_records_data:
        sid, date, sbp, dbp, sugar, hr, status = rec
        # 构造兼容 elderly_id（E开头）
        elderly_id = f'E{sid:05d}'
        cursor.execute('''
        INSERT OR IGNORE INTO health_record (elderly_id, record_date, sbp, dbp, blood_sugar, heart_rate, health_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (elderly_id, date, sbp, dbp, sugar, hr, status))
    
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

    # 同步插入兼容的 service_record 表
    for rec in service_records_data:
        sid, sdate, stype, duration, satis, comm = rec
        elderly_id = f'E{sid:05d}'
        cursor.execute('''
        INSERT OR IGNORE INTO service_record (elderly_id, community_id, service_type, service_date, duration, satisfaction)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (elderly_id, comm, stype, sdate, duration, satis))
    
    # 提交更改
    conn.commit()
    # 在插入兼容表之前，确保兼容表的列存在（对存在的旧表进行列补齐）
    def ensure_columns(table_name, cols):
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing = [r[1] for r in cursor.fetchall()]
        except Exception:
            existing = []
        for col_name, col_def in cols.items():
            if col_name not in existing:
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
                except Exception:
                    # 如果表不存在或无法添加，忽略并继续
                    pass

    # health_record 需要的列
    ensure_columns('health_record', {
        'elderly_id': 'TEXT',
        'record_date': 'TEXT',
        'sbp': 'INTEGER',
        'dbp': 'INTEGER',
        'blood_sugar': 'REAL',
        'heart_rate': 'INTEGER',
        'health_status': 'TEXT'
    })

    # service_record 需要的列
    ensure_columns('service_record', {
        'elderly_id': 'TEXT',
        'community_id': 'TEXT',
        'service_type': 'TEXT',
        'service_date': 'TEXT',
        'duration': 'INTEGER',
        'satisfaction': 'INTEGER'
    })

    # elderly 需要的列
    ensure_columns('elderly', {
        'elderly_id': 'TEXT',
        'name': 'TEXT',
        'age': 'INTEGER',
        'gender': 'TEXT',
        'community_id': 'TEXT'
    })

    conn.commit()
    conn.close()
    
    print("数据库初始化成功！")

if __name__ == '__main__':
    init_db()
