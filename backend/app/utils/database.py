"""数据库工具模块

管理数据库连接和基本操作
"""

import sqlite3
import os
from app.config.config import current_config

class Database:
    """数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_path = current_config.DATABASE_PATH
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
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
        query = f"PRAGMA table_info({table_name});"
        return self.execute(query)

# 全局数据库实例
db = Database()
