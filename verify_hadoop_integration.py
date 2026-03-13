#!/usr/bin/env python3
"""
Hadoop集成验证脚本

验证Hadoop、Hive、HBase的安装和配置是否成功
"""

import os
import sys
import time

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_hadoop_status():
    """检查Hadoop状态"""
    print("=== 检查Hadoop状态 ===")
    try:
        # 检查HDFS状态
        import subprocess
        result = subprocess.run(['hdfs', 'dfsadmin', '-report'], 
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ HDFS状态正常")
        else:
            print("❌ HDFS状态异常:", result.stderr)
            return False
        
        # 检查YARN状态
        result = subprocess.run(['yarn', 'node', '-list'], 
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ YARN状态正常")
        else:
            print("❌ YARN状态异常:", result.stderr)
            return False
        
        return True
    except Exception as e:
        print("❌ 检查Hadoop状态失败:", e)
        return False

def check_hbase_status():
    """检查HBase状态"""
    print("\n=== 检查HBase状态 ===")
    try:
        # 检查HBase状态
        import subprocess
        result = subprocess.run(['hbase', 'shell', '-c', 'status'], 
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ HBase状态正常")
        else:
            print("❌ HBase状态异常:", result.stderr)
            return False
        
        # 检查HBase表
        result = subprocess.run(['hbase', 'shell', '-c', 'list'], 
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ HBase表检查成功")
            print("表列表:", result.stdout)
        else:
            print("❌ HBase表检查失败:", result.stderr)
            return False
        
        return True
    except Exception as e:
        print("❌ 检查HBase状态失败:", e)
        return False

def check_hive_status():
    """检查Hive状态"""
    print("\n=== 检查Hive状态 ===")
    try:
        # 检查Hive服务
        import subprocess
        result = subprocess.run(['hive', '-e', 'SHOW DATABASES;'], 
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Hive状态正常")
        else:
            print("❌ Hive状态异常:", result.stderr)
            return False
        
        # 检查Hive表
        result = subprocess.run(['hive', '-e', 'USE elderly_care; SHOW TABLES;'], 
                               capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Hive表检查成功")
            print("表列表:", result.stdout)
        else:
            print("❌ Hive表检查失败:", result.stderr)
            return False
        
        return True
    except Exception as e:
        print("❌ 检查Hive状态失败:", e)
        return False

def check_data_migration():
    """检查数据迁移"""
    print("\n=== 检查数据迁移 ===")
    try:
        # 检查SQLite数据
        import sqlite3
        db_path = os.path.join('backend', 'data', 'database', 'elderly_care.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 统计SQLite中的数据量
        cursor.execute("SELECT COUNT(*) FROM seniors;")
        sqlite_seniors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM health_records;")
        sqlite_health = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM service_records;")
        sqlite_service = cursor.fetchone()[0]
        conn.close()
        
        print(f"SQLite数据: 老人={sqlite_seniors}, 健康记录={sqlite_health}, 服务记录={sqlite_service}")
        
        # 检查HBase数据
        from backend.app.utils.database import db
        os.environ['USE_HADOOP'] = 'True'
        
        # 统计HBase中的数据量
        try:
            # 使用Hive查询HBase数据
            hive_seniors = db.execute("SELECT COUNT(*) FROM seniors;")[0][0]
            hive_health = db.execute("SELECT COUNT(*) FROM health_records;")[0][0]
            hive_service = db.execute("SELECT COUNT(*) FROM service_records;")[0][0]
            
            print(f"HBase数据: 老人={hive_seniors}, 健康记录={hive_health}, 服务记录={hive_service}")
            
            # 验证数据一致性
            if (sqlite_seniors == hive_seniors and 
                sqlite_health == hive_health and 
                sqlite_service == hive_service):
                print("✅ 数据迁移成功，数据一致性验证通过")
                return True
            else:
                print("❌ 数据迁移失败，数据不一致")
                return False
        except Exception as e:
            print("❌ 检查HBase数据失败:", e)
            return False
            
    except Exception as e:
        print("❌ 检查数据迁移失败:", e)
        return False

def check_api_availability():
    """检查API可用性"""
    print("\n=== 检查API可用性 ===")
    try:
        # 启动后端服务
        import subprocess
        import time
        
        # 启动服务
        process = subprocess.Popen(['python', 'backend/app.py'], 
                                  cwd=os.path.dirname(os.path.abspath(__file__)),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        time.sleep(5)
        
        # 检查服务是否启动成功
        import requests
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=10)
            if response.status_code == 200:
                print("✅ API服务正常")
                print("健康检查响应:", response.json())
                process.terminate()
                return True
            else:
                print("❌ API服务异常:", response.status_code)
                process.terminate()
                return False
        except Exception as e:
            print("❌ API服务不可用:", e)
            process.terminate()
            return False
            
    except Exception as e:
        print("❌ 检查API可用性失败:", e)
        return False

def main():
    """主函数"""
    print("开始验证Hadoop集成...\n")
    
    # 检查Hadoop状态
    hadoop_ok = check_hadoop_status()
    
    # 检查HBase状态
    hbase_ok = check_hbase_status()
    
    # 检查Hive状态
    hive_ok = check_hive_status()
    
    # 检查数据迁移
    migration_ok = check_data_migration()
    
    # 检查API可用性
    api_ok = check_api_availability()
    
    print("\n=== 验证结果汇总 ===")
    print(f"Hadoop状态: {'✅ 正常' if hadoop_ok else '❌ 异常'}")
    print(f"HBase状态: {'✅ 正常' if hbase_ok else '❌ 异常'}")
    print(f"Hive状态: {'✅ 正常' if hive_ok else '❌ 异常'}")
    print(f"数据迁移: {'✅ 成功' if migration_ok else '❌ 失败'}")
    print(f"API可用性: {'✅ 正常' if api_ok else '❌ 异常'}")
    
    # 检查是否所有验证都通过
    if all([hadoop_ok, hbase_ok, hive_ok, migration_ok, api_ok]):
        print("\n🎉 所有验证都通过！Hadoop集成成功。")
        return 0
    else:
        print("\n❌ 部分验证失败，请检查相关配置。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
