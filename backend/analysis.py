""" 老年人护理需求预测系统 - 主入口文件
将原有路由结构与新增的 HBase/Hive 接口完美融合的最终版本
"""

import os
import sys

# 1. 将当前目录添加到系统路径，保证包导入正常
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== 核心修改点：不要自己创建 Flask(__name__) ==========
# 2. 从 app 包中导入已经初始化好、并注册了所有蓝图（包括 indicators 等）的 Flask 应用实例
from app import app 
from flask import jsonify
import happybase
from pyhive import hive

# ========== 3. 配置大数据连接 ==========
HIVE_HOST = "localhost"  # Hive 服务器地址
HIVE_PORT = 10000        # Hive 默认端口
HIVE_DB = "elderly_care" # 数据库名

HBASE_HOST = "localhost" # HBase 服务器地址
HBASE_PORT = 9090        # HBase Thrift 端口
HBASE_TABLE = "elderly_health_record"  
HBASE_CF = "health"      

# ========== 4. 在原有的 app 实例上挂载新增接口 ==========
@app.route('/api/elderly/<elderly_id>', methods=['GET'])
def get_elderly_info(elderly_id):
    """接口1：查询老人基本信息（从 Hive 读取）"""
    try:
        hive_conn = hive.Connection(host=HIVE_HOST, port=HIVE_PORT, database=HIVE_DB)
        hive_cursor = hive_conn.cursor()
        hive_cursor.execute(f"SELECT elderly_id, name, age, gender, community_id FROM elderly WHERE elderly_id = '{elderly_id}'")
        result = hive_cursor.fetchone()
        hive_conn.close()
        
        if not result:
            return jsonify({"code": 404, "msg": "未找到该老人的信息", "data": None}), 404
        
        elderly_data = {
            "elderly_id": result[0], "name": result[1], "age": result[2],
            "gender": result[3], "community_id": result[4]
        }
        return jsonify({"code": 200, "msg": "查询成功", "data": elderly_data}), 200
    except Exception as e:
        return jsonify({"code": 500, "msg": f"查询失败：{str(e)}", "data": None}), 500


@app.route('/api/elderly/health/<elderly_id>', methods=['GET'])
def get_elderly_health(elderly_id):
    """接口2：查询老人健康记录（从 HBase 读取）"""
    try:
        hbase_conn = happybase.Connection(HBASE_HOST, port=HBASE_PORT)
        health_table = hbase_conn.table(HBASE_TABLE)
        health_records = []
        for rowkey, row_data in health_table.scan(row_prefix=elderly_id.encode('utf-8')):
            record = {
                "rowkey": rowkey.decode('utf-8'),
                "age": row_data[f"{HBASE_CF}:age".encode()].decode('utf-8'),
                "gender": row_data[f"{HBASE_CF}:gender".encode()].decode('utf-8'),
                "community_id": row_data[f"{HBASE_CF}:community_id".encode()].decode('utf-8'),
                "health_status": row_data[f"{HBASE_CF}:health_status".encode()].decode('utf-8')
            }
            health_records.append(record)
        hbase_conn.close()
        
        return jsonify({"code": 200, "msg": "查询成功", "count": len(health_records), "data": health_records}), 200
    except Exception as e:
        return jsonify({"code": 500, "msg": f"查询失败：{str(e)}", "data": None}), 500

# ========== 5. 唯一正确的启动入口 ==========
if __name__ == '__main__':
    """应用入口：启动Flask服务"""
    # 确保此处只有一次 app.run 调用，并且绑定 0.0.0.0 和端口 5008
    app.run(debug=True, port=5008, host='0.0.0.0')