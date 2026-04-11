#!/usr/bin/env python3
import os
import sys
import sqlite3
import time
from pyhive import hive
import happybase

SQLITE_DB_PATH = os.environ.get(
    "SQLITE_DB_PATH",
    "/opt/bigdata/flask_elderly_care/backend/data/database/elderly_care.db"
)
HIVE_HOST = os.environ.get("HIVE_HOST", "localhost")
HIVE_PORT = int(os.environ.get("HIVE_PORT", "10000"))
HIVE_DB = os.environ.get("HIVE_DATABASE", "elderly_care")
HBASE_HOST = os.environ.get("HBASE_HOST", "localhost")
HBASE_PORT = int(os.environ.get("HBASE_PORT", "9090"))
HBASE_TABLE = os.environ.get("HBASE_TABLE", "elderly_health_record")
HBASE_CF = os.environ.get("HBASE_CF", "health")

def _safe_text(value, default="未知"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default

def _get_sqlite_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row[0] for row in cursor.fetchall()}

def _read_profile_legacy(cursor):
    cursor.execute("SELECT elderly_id, name, age, gender, community_id FROM elderly")
    elderly = cursor.fetchall()
    cursor.execute("SELECT elderly_id, age, gender, community_id, health_status, record_date FROM health_record")
    health = cursor.fetchall()
    cursor.execute("SELECT elderly_id, community_id, service_type, service_date, satisfaction FROM service_record")
    service = cursor.fetchall()
    if "community" in _get_sqlite_tables(cursor):
        cursor.execute("SELECT community_id, name, population, elderly_count FROM community")
        community = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT community_id, community_id, COUNT(*), COUNT(*)
            FROM elderly
            GROUP BY community_id
        """)
        community = cursor.fetchall()
    return elderly, health, service, community, "legacy"

def read_sqlite():
    if not os.path.exists(SQLITE_DB_PATH):
        print("❌ SQLite database file not found!")
        return None
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        tables = _get_sqlite_tables(cursor)

        if {"elderly", "health_record", "service_record"}.issubset(tables):
            elderly, health, service, community, profile = _read_profile_legacy(cursor)
        else:
            conn.close()
            print("❌ Unsupported SQLite schema, available tables:", sorted(tables))
            return None
        conn.close()

        print(f"✅ Read data completed, profile={profile}")
        print(f"  - Elderly: {len(elderly)} records")
        print(f"  - Health records: {len(health)} records")
        print(f"  - Service records: {len(service)} records")
        print(f"  - Community: {len(community)} records")

        return {"elderly": elderly, "health": health, "service": service, "community": community}
    except Exception as e:
        print(f"❌ Read SQLite failed: {str(e)}")
        return None

def _hive_connect_with_retry(retries=5, sleep_seconds=3):
    last_error = None
    for _ in range(retries):
        try:
            return hive.Connection(host=HIVE_HOST, port=HIVE_PORT)
        except Exception as e:
            last_error = e
            time.sleep(sleep_seconds)
    raise last_error

def _hbase_connect_with_retry(retries=5, sleep_seconds=3):
    last_error = None
    for _ in range(retries):
        try:
            conn = happybase.Connection(HBASE_HOST, port=HBASE_PORT, timeout=10000)
            conn.tables()
            return conn
        except Exception as e:
            last_error = e
            time.sleep(sleep_seconds)
    raise last_error

# 【终极修复】使用 LOAD DATA LOCAL INPATH 直接进行物理文件移动，彻底绕过 MapReduce 引擎！
def _load_hive_via_file(cursor, table_name, rows):
    if not rows:
        return
    tmp_file = f"/tmp/{table_name}_export.csv"
    
    # 1. 把数据写成本地 CSV 文件
    with open(tmp_file, 'w', encoding='utf-8') as f:
        for row in rows:
            clean_row = []
            for val in row:
                if val is None:
                    clean_row.append("")
                else:
                    # 避免数据自带的逗号破坏 CSV 结构
                    val_str = str(val).replace(",", "，").replace("\n", " ")
                    clean_row.append(val_str)
            f.write(",".join(clean_row) + "\n")
    
    # 2. 直接命令 Hive 把文件放进 HDFS 仓库，秒级完成！
    cursor.execute(f"LOAD DATA LOCAL INPATH '{tmp_file}' OVERWRITE INTO TABLE {table_name}")
    
    # 3. 清理临时文件
    try:
        os.remove(tmp_file)
    except:
        pass

def export_to_hive(data):
    if not data:
        return False
    try:
        hive_conn = _hive_connect_with_retry()
        hive_cursor = hive_conn.cursor()

        hive_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {HIVE_DB}")
        hive_cursor.execute(f"USE {HIVE_DB}")

        hive_cursor.execute("CREATE TABLE IF NOT EXISTS elderly (elderly_id STRING, name STRING, age INT, gender STRING, community_id STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','")
        hive_cursor.execute("CREATE TABLE IF NOT EXISTS health_record (elderly_id STRING, age INT, gender STRING, community_id STRING, health_status STRING, record_date STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','")
        hive_cursor.execute("CREATE TABLE IF NOT EXISTS service_record (elderly_id STRING, community_id STRING, service_type STRING, service_date STRING, satisfaction INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','")
        hive_cursor.execute("CREATE TABLE IF NOT EXISTS community (community_id STRING, name STRING, population INT, elderly_count INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','")

        # 使用文件直传方式导入数据
        _load_hive_via_file(hive_cursor, "elderly", data["elderly"])
        _load_hive_via_file(hive_cursor, "health_record", data["health"])
        _load_hive_via_file(hive_cursor, "service_record", data["service"])
        _load_hive_via_file(hive_cursor, "community", data["community"])

        hive_conn.commit()
        hive_conn.close()
        print("✅ Hive data export completed via fast file-load!")
        return True
    except Exception as e:
        print(f"❌ Export to Hive failed: {str(e)}")
        return False

def export_to_hbase(data):
    if not data or not data["health"]:
        return False
    try:
        hbase_conn = _hbase_connect_with_retry()
        existing_tables = hbase_conn.tables()
        if HBASE_TABLE.encode("utf-8") not in existing_tables:
            hbase_conn.create_table(HBASE_TABLE, {HBASE_CF: dict()})

        table = hbase_conn.table(HBASE_TABLE)
        batch = table.batch()
        for row in data["health"]:
            elderly_id = _safe_text(row[0], "UNKNOWN")
            record_date = _safe_text(row[5], "1970-01-01")
            rowkey = f"{elderly_id}_{record_date}".encode("utf-8")
            put_data = {
                f"{HBASE_CF}:age".encode("utf-8"): str(int(row[1] if row[1] is not None else 0)).encode("utf-8"),
                f"{HBASE_CF}:gender".encode("utf-8"): _safe_text(row[2]).encode("utf-8"),
                f"{HBASE_CF}:community_id".encode("utf-8"): _safe_text(row[3], "UNKNOWN").encode("utf-8"),
                f"{HBASE_CF}:health_status".encode("utf-8"): _safe_text(row[4], "未知").encode("utf-8")
            }
            batch.put(rowkey, put_data)

        batch.send()
        hbase_conn.close()
        print(f"✅ HBase data export completed! Total {len(data['health'])} health records exported")
        return True
    except Exception as e:
        print(f"❌ Export to HBase failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("===== Start exporting data from SQLite to Hive/HBase =====")
    data = read_sqlite()
    if not data:
        sys.exit(1)
    hive_ok = export_to_hive(data)
    hbase_ok = export_to_hbase(data)
    print("===== Data export process completed! =====")
    sys.exit(0 if hive_ok and hbase_ok else 1)