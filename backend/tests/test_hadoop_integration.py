"""Hadoop集成测试脚本

测试HBase和Hive的连接和操作
"""

import unittest
import os
import sys
import time
from app.utils.database import db
from app.utils.hadoop_database import hadoop_db

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestHadoopIntegration(unittest.TestCase):
    """Hadoop集成测试类"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 启用Hadoop数据库
        os.environ['USE_HADOOP'] = 'True'
        # 重新初始化数据库实例
        global db
        from app.utils.database import Database
        db = Database()
    
    def test_hbase_connection(self):
        """测试HBase连接"""
        try:
            connection = hadoop_db.get_hbase_connection()
            self.assertIsNotNone(connection)
            print("✅ HBase连接测试通过")
        except Exception as e:
            self.fail(f"HBase连接失败: {e}")
    
    def test_hive_connection(self):
        """测试Hive连接"""
        try:
            connection = hadoop_db.get_hive_connection()
            self.assertIsNotNone(connection)
            print("✅ Hive连接测试通过")
        except Exception as e:
            self.fail(f"Hive连接失败: {e}")
    
    def test_hbase_table_exists(self):
        """测试HBase表是否存在"""
        try:
            connection = hadoop_db.get_hbase_connection()
            tables = connection.tables()
            expected_tables = [b'seniors', b'health_records', b'service_records']
            for table in expected_tables:
                self.assertIn(table, tables)
            print("✅ HBase表存在测试通过")
        except Exception as e:
            self.fail(f"HBase表检查失败: {e}")
    
    def test_hive_table_exists(self):
        """测试Hive表是否存在"""
        try:
            result = db.execute("SHOW TABLES;")
            tables = [row[0] for row in result]
            expected_tables = ['seniors', 'health_records', 'service_records']
            for table in expected_tables:
                self.assertIn(table, tables)
            print("✅ Hive表存在测试通过")
        except Exception as e:
            self.fail(f"Hive表检查失败: {e}")
    
    def test_hbase_get_data(self):
        """测试从HBase获取数据"""
        try:
            # 测试获取老人数据
            result = db.hbase_get('seniors', 'senior:1')
            self.assertIsInstance(result, dict)
            self.assertIn(b'info:age', result)
            print("✅ HBase数据获取测试通过")
        except Exception as e:
            self.fail(f"HBase数据获取失败: {e}")
    
    def test_hbase_scan_data(self):
        """测试扫描HBase数据"""
        try:
            # 测试扫描老人数据
            result = db.hbase_scan('seniors', limit=5)
            self.assertIsInstance(result, list)
            self.assertTrue(len(result) > 0)
            print("✅ HBase数据扫描测试通过")
        except Exception as e:
            self.fail(f"HBase数据扫描失败: {e}")
    
    def test_hive_query(self):
        """测试Hive查询"""
        try:
            # 测试查询老人数量
            result = db.execute("SELECT COUNT(*) FROM seniors;")
            self.assertIsInstance(result, list)
            self.assertTrue(len(result) > 0)
            print("✅ Hive查询测试通过")
        except Exception as e:
            self.fail(f"Hive查询失败: {e}")
    
    def test_performance(self):
        """测试性能"""
        try:
            # 测试HBase查询性能
            start_time = time.time()
            for i in range(10):
                db.hbase_get('seniors', f'senior:{i+1}')
            hbase_time = time.time() - start_time
            print(f"✅ HBase性能测试通过，10次查询耗时: {hbase_time:.2f}秒")
            
            # 测试Hive查询性能
            start_time = time.time()
            db.execute("SELECT * FROM seniors LIMIT 10;")
            hive_time = time.time() - start_time
            print(f"✅ Hive性能测试通过，查询耗时: {hive_time:.2f}秒")
        except Exception as e:
            self.fail(f"性能测试失败: {e}")

class TestDataMigration(unittest.TestCase):
    """数据迁移测试类"""
    
    def test_data_consistency(self):
        """测试数据一致性"""
        try:
            # 从SQLite获取数据
            os.environ['USE_HADOOP'] = 'False'
            from app.utils.database import Database
            sqlite_db = Database()
            sqlite_seniors = sqlite_db.execute("SELECT COUNT(*) FROM seniors;")[0][0]
            
            # 从Hadoop获取数据
            os.environ['USE_HADOOP'] = 'True'
            hadoop_db = Database()
            hadoop_seniors = hadoop_db.execute("SELECT COUNT(*) FROM seniors;")[0][0]
            
            # 验证数据一致性
            self.assertEqual(sqlite_seniors, hadoop_seniors)
            print("✅ 数据一致性测试通过")
        except Exception as e:
            self.fail(f"数据一致性测试失败: {e}")

if __name__ == '__main__':
    unittest.main()
