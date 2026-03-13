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
