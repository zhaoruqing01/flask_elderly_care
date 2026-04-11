#!/usr/bin/env python3

import os
import sys
import time
import sqlite3
import subprocess
import urllib.request
import urllib.error

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
HIVE_DB = os.environ.get("HIVE_DATABASE", "elderly_care")
SQLITE_DB_PATH = os.environ.get(
    "SQLITE_DB_PATH",
    "/opt/bigdata/flask_elderly_care/backend/data/database/elderly_care.db"
)


def _run_cmd(command, timeout=40):
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=timeout
    )


def check_hadoop_status():
    print("=== 检查Hadoop状态 ===")
    try:
        result = _run_cmd(["hdfs", "dfsadmin", "-report"])
        if result.returncode != 0:
            print("❌ HDFS状态异常:", result.stderr.strip())
            return False
        print("✅ HDFS状态正常")

        result = _run_cmd(["yarn", "node", "-list"])
        if result.returncode != 0:
            print("❌ YARN状态异常:", result.stderr.strip())
            return False
        print("✅ YARN状态正常")
        return True
    except Exception as e:
        print("❌ 检查Hadoop状态失败:", str(e))
        return False


def check_hbase_status():
    print("\n=== 检查HBase状态 ===")
    try:
        result = _run_cmd(["hbase", "shell", "-c", "status"])
        if result.returncode != 0:
            print("❌ HBase状态异常:", result.stderr.strip())
            return False
        print("✅ HBase状态正常")

        result = _run_cmd(["hbase", "shell", "-c", "list"])
        if result.returncode != 0:
            print("❌ HBase表检查失败:", result.stderr.strip())
            return False
        print("✅ HBase表检查成功")
        return True
    except Exception as e:
        print("❌ 检查HBase状态失败:", str(e))
        return False


def check_hive_status():
    print("\n=== 检查Hive状态 ===")
    try:
        result = _run_cmd(["hive", "-e", "SHOW DATABASES;"])
        if result.returncode != 0:
            print("❌ Hive状态异常:", result.stderr.strip())
            return False
        print("✅ Hive状态正常")

        result = _run_cmd(["hive", "-e", f"USE {HIVE_DB}; SHOW TABLES;"])
        if result.returncode != 0:
            print("❌ Hive表检查失败:", result.stderr.strip())
            return False
        print("✅ Hive表检查成功")
        return True
    except Exception as e:
        print("❌ 检查Hive状态失败:", str(e))
        return False


def _sqlite_counts():
    if not os.path.exists(SQLITE_DB_PATH):
        raise FileNotFoundError(f"SQLite数据库不存在: {SQLITE_DB_PATH}")

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    if {"elderly", "health_record", "service_record"}.issubset(tables):
        queries = {
            "elderly": "SELECT COUNT(*) FROM elderly",
            "health_record": "SELECT COUNT(*) FROM health_record",
            "service_record": "SELECT COUNT(*) FROM service_record"
        }
    elif {"seniors", "health_records", "service_records"}.issubset(tables):
        queries = {
            "elderly": "SELECT COUNT(*) FROM seniors",
            "health_record": "SELECT COUNT(*) FROM health_records",
            "service_record": "SELECT COUNT(*) FROM service_records"
        }
    elif {"senior", "health_record", "service_log"}.issubset(tables):
        queries = {
            "elderly": "SELECT COUNT(*) FROM senior",
            "health_record": "SELECT COUNT(*) FROM health_record",
            "service_record": "SELECT COUNT(*) FROM service_log"
        }
    else:
        conn.close()
        raise RuntimeError(f"无法识别SQLite表结构: {sorted(tables)}")

    result = {}
    for key, query in queries.items():
        cursor.execute(query)
        result[key] = int(cursor.fetchone()[0])
    conn.close()
    return result


def _hive_count(table_name):
    result = _run_cmd(["hive", "-e", f"USE {HIVE_DB}; SELECT COUNT(*) FROM {table_name};"], timeout=60)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    number_lines = [line for line in lines if line.isdigit()]
    if not number_lines:
        raise RuntimeError(f"Hive输出无法解析计数: {result.stdout}")
    return int(number_lines[-1])


def check_data_migration():
    print("\n=== 检查数据迁移 ===")
    try:
        sqlite_result = _sqlite_counts()
        print(
            f"SQLite数据: 老人={sqlite_result['elderly']}, "
            f"健康记录={sqlite_result['health_record']}, "
            f"服务记录={sqlite_result['service_record']}"
        )

        hive_result = {
            "elderly": _hive_count("elderly"),
            "health_record": _hive_count("health_record"),
            "service_record": _hive_count("service_record")
        }
        print(
            f"Hive数据: 老人={hive_result['elderly']}, "
            f"健康记录={hive_result['health_record']}, "
            f"服务记录={hive_result['service_record']}"
        )

        if sqlite_result == hive_result:
            print("✅ 数据迁移成功，字段对应后的数据量一致")
            return True
        print("❌ 数据迁移失败，数据量不一致")
        return False
    except Exception as e:
        print("❌ 检查数据迁移失败:", str(e))
        return False


def _probe_api():
    target = "http://127.0.0.1:5008/api/elderly/NOT_EXIST"
    try:
        urllib.request.urlopen(target, timeout=2)
        return True
    except urllib.error.HTTPError as e:
        return e.code in (200, 404)
    except Exception:
        return False


def check_api_availability():
    print("\n=== 检查API可用性 ===")
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, "backend/app.py"],
            cwd=PROJECT_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(25):
            time.sleep(1)
            if _probe_api():
                print("✅ API服务正常（端口5008）")
                return True
        print("❌ API服务不可用（端口5008）")
        return False
    except Exception as e:
        print("❌ 检查API可用性失败:", str(e))
        return False
    finally:
        if process is not None:
            process.terminate()


def main():
    print("开始验证Hadoop集成...\n")

    hadoop_ok = check_hadoop_status()
    hbase_ok = check_hbase_status()
    hive_ok = check_hive_status()
    migration_ok = check_data_migration()
    api_ok = check_api_availability()

    print("\n=== 验证结果汇总 ===")
    print(f"Hadoop状态: {'✅ 正常' if hadoop_ok else '❌ 异常'}")
    print(f"HBase状态: {'✅ 正常' if hbase_ok else '❌ 异常'}")
    print(f"Hive状态: {'✅ 正常' if hive_ok else '❌ 异常'}")
    print(f"数据迁移: {'✅ 成功' if migration_ok else '❌ 失败'}")
    print(f"API可用性: {'✅ 正常' if api_ok else '❌ 异常'}")

    if all([hadoop_ok, hbase_ok, hive_ok, migration_ok, api_ok]):
        print("\n🎉 所有验证都通过！Hadoop集成成功。")
        return 0
    print("\n❌ 部分验证失败，请检查相关配置。")
    return 1


if __name__ == '__main__':
    sys.exit(main())
