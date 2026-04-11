"""Hadoop数据库工具模块

管理HBase和Hive连接和基本操作
"""

import happybase
from pyhive import hive
import os
from app.config.config import current_config

class HadoopDatabase:
    """Hadoop数据库管理类"""
    
    def __init__(self):
        """初始化Hadoop数据库连接"""
        self.hbase_host = os.environ.get('HBASE_HOST', 'hadoop-master')
        self.hive_host = os.environ.get('HIVE_HOST', 'hadoop-master')
        self.hive_port = int(os.environ.get('HIVE_PORT', '10000'))
        self.hive_database = os.environ.get('HIVE_DATABASE', 'elderly_care')
        
        # HBase连接
        self.hbase_connection = None
        # Hive连接
        self.hive_connection = None
        self.hive_cursor = None
    
    def get_hbase_connection(self):
        """
        获取HBase连接
        
        返回值：
        - happybase.Connection: HBase连接对象
        """
        if not self.hbase_connection:
            self.hbase_connection = happybase.Connection(self.hbase_host)
            self.hbase_connection.open()
        return self.hbase_connection
    
    def get_hive_connection(self):
        """
        获取Hive连接
        
        返回值：
        - hive.Connection: Hive连接对象
        """
        if not self.hive_connection:
            self.hive_connection = hive.Connection(
                host=self.hive_host,
                port=self.hive_port,
                database=self.hive_database
            )
            self.hive_cursor = self.hive_connection.cursor()
        return self.hive_connection
    
    def get_hive_cursor(self):
        """
        获取Hive游标
        
        返回值：
        - hive.Cursor: Hive游标对象
        """
        if not self.hive_cursor:
            self.get_hive_connection()
        return self.hive_cursor
    
    # HBase操作方法
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
        connection = self.get_hbase_connection()
        table = connection.table(table_name)
        return table.row(row_key, columns)
    
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
        connection = self.get_hbase_connection()
        table = connection.table(table_name)
        scanner = table.scan(row_start=row_start, row_stop=row_stop, columns=columns, limit=limit)
        return list(scanner)
    
    def hbase_put(self, table_name, row_key, data):
        """
        向HBase表中插入数据
        
        参数：
        - table_name: 表名
        - row_key: 行键
        - data: 数据字典
        """
        connection = self.get_hbase_connection()
        table = connection.table(table_name)
        table.put(row_key, data)
    
    def hbase_delete(self, table_name, row_key, columns=None):
        """
        从HBase表中删除数据
        
        参数：
        - table_name: 表名
        - row_key: 行键
        - columns: 列列表（可选）
        """
        connection = self.get_hbase_connection()
        table = connection.table(table_name)
        table.delete(row_key, columns)
    
    # Hive操作方法
    def hive_execute(self, query, params=None):
        """
        执行Hive SQL查询
        
        参数：
        - query: SQL查询语句
        - params: 查询参数（可选）
        
        返回值：
        - list: 查询结果（如果是SELECT语句）
        """
        cursor = self.get_hive_cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # 如果是SELECT语句，返回结果
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                result = None
        finally:
            pass
        
        return result
    
    def hive_execute_many(self, query, params_list):
        """
        批量执行Hive SQL查询
        
        参数：
        - query: SQL查询语句
        - params_list: 查询参数列表
        """
        cursor = self.get_hive_cursor()
        cursor.executemany(query, params_list)
    
    def close(self):
        """
        关闭所有连接
        """
        if self.hbase_connection:
            self.hbase_connection.close()
        if self.hive_connection:
            self.hive_cursor.close()
            self.hive_connection.close()

# 全局Hadoop数据库实例
hadoop_db = HadoopDatabase()
