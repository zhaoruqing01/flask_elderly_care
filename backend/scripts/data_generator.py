#!/usr/bin/env python3
import sqlite3
import random
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database', 'elderly_care.db')

COMMUNITY_LIST = [("C001", "Community1", 5000, 800), ("C002", "Community2", 8000, 1200), ("C003", "Community3", 6000, 950)]
ELDERLY_GENDER = ["Male", "Female"]
HEALTH_STATUS = ["Healthy", "Hypertension", "Diabetes"]
SERVICE_TYPE = ["HomeCare", "HealthCheck", "Rehabilitation"]
SATISFACTION = [1,2,3,4,5]
ELDERLY_NAMES = ["ZhangSan", "LiSi", "WangWu"]

def generate_and_insert():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert community
    for c in COMMUNITY_LIST:
        cursor.execute("INSERT OR IGNORE INTO community (community_id, name, population, elderly_count) VALUES (?, ?, ?, ?)", c)
    
    # Insert elderly
    elderly_list = []
    for c in COMMUNITY_LIST:
        c_id = c[0]
        for i in range(10):  # 简化：每个社区只生成10个老人，减少数据量
            e_id = f"E{c_id[-3:]}{str(i+1).zfill(2)}"
            name = ELDERLY_NAMES[i%3] + str(i+1)
            age = random.randint(60,90)
            gender = random.choice(ELDERLY_GENDER)
            elderly_list.append((e_id, name, age, gender, c_id))
            cursor.execute("INSERT OR IGNORE INTO elderly (elderly_id, name, age, gender, community_id) VALUES (?, ?, ?, ?, ?)", (e_id, name, age, gender, c_id))
    
    # Insert health record
    start_date = datetime.date(2026,1,1)
    health_records = []
    for e in elderly_list:
        e_id, _, age, gender, c_id = e
        for _ in range(2):
            r_date = start_date + datetime.timedelta(days=random.randint(0,30))
            h_status = random.choice(HEALTH_STATUS)
            health_records.append((e_id, age, gender, c_id, h_status, r_date))
    cursor.executemany("INSERT INTO health_record (elderly_id, age, gender, community_id, health_status, record_date) VALUES (?, ?, ?, ?, ?, ?)", health_records)
    
    # Insert service record
    service_records = []
    for e in elderly_list:
        e_id, _, _, _, c_id = e
        for _ in range(1):
            s_date = start_date + datetime.timedelta(days=random.randint(0,30))
            s_type = random.choice(SERVICE_TYPE)
            satis = random.choice(SATISFACTION)
            service_records.append((e_id, c_id, s_type, s_date, satis))
    cursor.executemany("INSERT INTO service_record (elderly_id, community_id, service_type, service_date, satisfaction) VALUES (?, ?, ?, ?, ?)", service_records)
    
    conn.commit()
    conn.close()
    print("Data generated successfully!")

if __name__ == '__main__':
    generate_and_insert()
