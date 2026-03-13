"""管理服务模块

处理数据生成、清洗、模型训练等管理功能
"""

import os
import sys
from app.config.config import current_config

# 添加backend目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_generator import generate_and_insert
from data_cleaner import clean_all_data
from predictor import train_model

class AdminService:
    """管理服务类"""
    
    def generate_data(self):
        """
        生成模拟数据
        """
        generate_and_insert()
    
    def clean_data(self):
        """
        清洗数据
        
        返回值：
        - dict: 清洗统计数据
        """
        return clean_all_data()
    
    def train_model(self):
        """
        训练模型
        
        返回值：
        - dict: 模型评估指标
        """
        _, metrics = train_model()
        return metrics
    
    def get_logs(self):
        """
        获取操作日志
        
        返回值：
        - list: 操作日志列表
        """
        # 模拟日志数据
        import datetime
        logs = [
            {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "生成数据",
                "status": "成功",
                "message": "成功生成300条老人信息和相关记录"
            },
            {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "清洗数据",
                "status": "成功",
                "message": "清洗了5条异常记录"
            },
            {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "训练模型",
                "status": "成功",
                "message": "模型训练完成，R²评分0.85"
            }
        ]
        return logs
    
    def get_data_quality(self):
        """
        获取数据质量信息
        
        返回值：
        - list: 数据质量列表
        """
        # 模拟数据质量数据
        data_quality = [
            {"name": "老人信息", "count": 300, "missing": 0, "quality": "良好"},
            {"name": "健康记录", "count": 1250, "missing": 5, "quality": "良好"},
            {"name": "服务记录", "count": 850, "missing": 2, "quality": "良好"},
            {"name": "预测结果", "count": 100, "missing": 0, "quality": "良好"}
        ]
        return data_quality
