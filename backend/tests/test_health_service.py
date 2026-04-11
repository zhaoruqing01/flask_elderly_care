"""健康服务测试

测试健康服务相关功能
"""

import unittest
from app.services.health_service import HealthService

class TestHealthService(unittest.TestCase):
    """健康服务测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.health_service = HealthService()
    
    def test_get_health_distribution(self):
        """测试获取健康状态分布"""
        result = self.health_service.get_health_distribution()
        self.assertIsInstance(result, dict)
        self.assertIn('labels', result)
        self.assertIn('values', result)
        self.assertEqual(len(result['labels']), 5)
        self.assertEqual(len(result['values']), 5)
    
    def test_get_health_distribution_by_age(self):
        """测试按年龄段分析健康状态分布"""
        result = self.health_service.get_health_distribution_by_age()
        self.assertIsInstance(result, dict)
        self.assertIn('age_groups', result)
        self.assertIn('health_statuses', result)
        self.assertIn('data', result)
        self.assertEqual(len(result['age_groups']), 5)
        self.assertEqual(len(result['health_statuses']), 5)
    
    def test_get_health_trend(self):
        """测试获取健康状态趋势"""
        result = self.health_service.get_health_trend()
        self.assertIsInstance(result, dict)
        self.assertIn('months', result)
        self.assertIn('data', result)

if __name__ == '__main__':
    unittest.main()
