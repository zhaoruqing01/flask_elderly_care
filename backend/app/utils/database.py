"""数据库工具模块

管理数据库连接和基本操作，支持SQLite和Hadoop数据库
"""

import sqlite3
import os
from app.config.config import current_config
from app.utils.hadoop_database import hadoop_db

class Database:
    """数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_path = current_config.DATABASE_PATH
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # 使用Hadoop数据库标志
        self.use_hadoop = os.environ.get('USE_HADOOP', 'False').lower() == 'true'
    
    def get_connection(self):
        """
        获取数据库连接
        
        返回值：
        - sqlite3.Connection: 数据库连接对象
        """
        return sqlite3.connect(self.db_path)
    
    def execute(self, query, params=None):
        """
        执行SQL查询
        
        参数：
        - query: SQL查询语句
        - params: 查询参数
        
        返回值：
        - list: 查询结果（如果是SELECT语句）
        """
        if self.use_hadoop:
            # 使用Hive执行查询
            return hadoop_db.hive_execute(query, params)
        else:
            # 使用SQLite执行查询
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # 如果是SELECT语句，返回结果
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = None
            finally:
                cursor.close()
                conn.close()
            
            return result
    
    def execute_many(self, query, params_list):
        """
        批量执行SQL查询
        
        参数：
        - query: SQL查询语句
        - params_list: 查询参数列表
        """
        if self.use_hadoop:
            # 使用Hive批量执行
            hadoop_db.hive_execute_many(query, params_list)
        else:
            # 使用SQLite批量执行
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.executemany(query, params_list)
                conn.commit()
            finally:
                cursor.close()
                conn.close()
    
    def get_tables(self):
        """
        获取数据库中的所有表
        
        返回值：
        - list: 表名列表
        """
        if self.use_hadoop:
            # 使用Hive获取表列表
            query = "SHOW TABLES;"
            result = hadoop_db.hive_execute(query)
            return [row[0] for row in result] if result else []
        else:
            # 使用SQLite获取表列表
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            result = self.execute(query)
            return [row[0] for row in result] if result else []
    
    def get_table_schema(self, table_name):
        """
        获取表的结构
        
        参数：
        - table_name: 表名
        
        返回值：
        - list: 表结构信息
        """
        if self.use_hadoop:
            # 使用Hive获取表结构
            query = f"DESCRIBE {table_name};"
            return hadoop_db.hive_execute(query)
        else:
            # 使用SQLite获取表结构
            query = f"PRAGMA table_info({table_name});"
            return self.execute(query)
    
    # HBase特定操作
    def hbase_get(self, table_name, row_key, columns=None):
        """
        从HBase表中获取数据
        
        参数：
        - table_name: 表名
        - row_key: 行键
        - columns: 列列表（可选）
        
        返回值：
        - dict: 查询结果
        """
        return hadoop_db.hbase_get(table_name, row_key, columns)
    
    def hbase_scan(self, table_name, row_start=None, row_stop=None, columns=None, limit=None):
        """
        扫描HBase表
        
        参数：
        - table_name: 表名
        - row_start: 起始行键（可选）
        - row_stop: 结束行键（可选）
        - columns: 列列表（可选）
        - limit: 限制返回数量（可选）
        
        返回值：
        - list: 查询结果列表
        """
        return hadoop_db.hbase_scan(table_name, row_start, row_stop, columns, limit)
    
    def hbase_put(self, table_name, row_key, data):
        """
        向HBase表中插入数据
        
        参数：
        - table_name: 表名
        - row_key: 行键
        - data: 数据字典
        """
        hadoop_db.hbase_put(table_name, row_key, data)
    
    def hbase_delete(self, table_name, row_key, columns=None):
        """
        从HBase表中删除数据
        
        参数：
        - table_name: 表名
        - row_key: 行键
        - columns: 列列表（可选）
        """
        hadoop_db.hbase_delete(table_name, row_key, columns)

# 全局数据库实例
db = Database()
