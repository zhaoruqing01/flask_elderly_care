#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级数据处理模块

该模块用于处理多种数据来源和复杂的预处理功能，包括：
1. 多数据源集成（CSV、Excel、API等）
2. 高级数据清洗和预处理
3. 特征工程和数据转换
4. 数据质量评估

使用说明：
- 运行 process_data() 函数处理数据
- 支持从多种来源加载数据
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import requests
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer, KNNImputer

# 数据库文件路径
DB_PATH = 'database/elderly_care.db'


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.db_path = DB_PATH
        self.scalers = {}
        self.imputers = {}
    
    def load_from_csv(self, file_path):
        """
        从CSV文件加载数据
        
        参数：
        - file_path: CSV文件路径
        
        返回值：
        - DataFrame: 加载的数据
        """
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            print(f"从CSV加载数据失败: {e}")
            return None
    
    def load_from_excel(self, file_path, sheet_name=0):
        """
        从Excel文件加载数据
        
        参数：
        - file_path: Excel文件路径
        - sheet_name: 工作表名称或索引
        
        返回值：
        - DataFrame: 加载的数据
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df
        except Exception as e:
            print(f"从Excel加载数据失败: {e}")
            return None
    
    def load_from_api(self, api_url, params=None):
        """
        从API加载数据
        
        参数：
        - api_url: API地址
        - params: 请求参数
        
        返回值：
        - DataFrame: 加载的数据
        """
        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                return df
            else:
                print(f"API请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"从API加载数据失败: {e}")
            return None
    
    def load_from_database(self, query):
        """
        从数据库加载数据
        
        参数：
        - query: SQL查询语句
        
        返回值：
        - DataFrame: 加载的数据
        """
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"从数据库加载数据失败: {e}")
            return None
    
    def clean_data(self, df, config=None):
        """
        高级数据清洗
        
        参数：
        - df: 待清洗的DataFrame
        - config: 清洗配置
        
        返回值：
        - DataFrame: 清洗后的数据
        """
        if df is None:
            return None
        
        # 默认配置
        default_config = {
            'remove_duplicates': True,
            'handle_missing': True,
            'outlier_detection': True,
            'normalize_dates': True,
            'scale_numeric': False
        }
        
        config = {**default_config, **(config or {})}
        
        # 复制数据以避免修改原数据
        cleaned_df = df.copy()
        
        # 删除重复行
        if config['remove_duplicates']:
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates()
            print(f"删除了 {initial_rows - len(cleaned_df)} 个重复行")
        
        # 处理缺失值
        if config['handle_missing']:
            # 识别数值列和分类列
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            categorical_cols = cleaned_df.select_dtypes(include=['object']).columns
            
            # 对数值列使用KNN imputer
            if len(numeric_cols) > 0:
                imputer = KNNImputer(n_neighbors=5)
                cleaned_df[numeric_cols] = imputer.fit_transform(cleaned_df[numeric_cols])
                self.imputers['numeric'] = imputer
            
            # 对分类列使用最频繁值填充
            if len(categorical_cols) > 0:
                for col in categorical_cols:
                    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
        
        # 异常值检测和处理
        if config['outlier_detection']:
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                # 使用IQR方法检测异常值
                Q1 = cleaned_df[col].quantile(0.25)
                Q3 = cleaned_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # 替换异常值为边界值
                cleaned_df[col] = cleaned_df[col].clip(lower=lower_bound, upper=upper_bound)
        
        # 标准化日期格式
        if config['normalize_dates']:
            date_cols = [col for col in cleaned_df.columns if 'date' in col.lower()]
            for col in date_cols:
                try:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                except Exception as e:
                    print(f"标准化日期列 {col} 失败: {e}")
        
        # 数值列标准化
        if config['scale_numeric']:
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            scaler = StandardScaler()
            cleaned_df[numeric_cols] = scaler.fit_transform(cleaned_df[numeric_cols])
            self.scalers['standard'] = scaler
        
        return cleaned_df
    
    def feature_engineering(self, df):
        """
        高级特征工程
        
        参数：
        - df: 原始DataFrame
        
        返回值：
        - DataFrame: 添加了特征的数据
        """
        if df is None:
            return None
        
        engineered_df = df.copy()
        
        # 日期特征
        date_cols = [col for col in engineered_df.columns if 'date' in col.lower()]
        for col in date_cols:
            if pd.api.types.is_datetime64_any_dtype(engineered_df[col]):
                engineered_df[f'{col}_year'] = engineered_df[col].dt.year
                engineered_df[f'{col}_month'] = engineered_df[col].dt.month
                engineered_df[f'{col}_day'] = engineered_df[col].dt.day
                engineered_df[f'{col}_dayofweek'] = engineered_df[col].dt.dayofweek
                engineered_df[f'{col}_is_weekend'] = (engineered_df[col].dt.dayofweek >= 5).astype(int)
                engineered_df[f'{col}_quarter'] = engineered_df[col].dt.quarter
        
        # 交互特征
        numeric_cols = engineered_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            for i in range(len(numeric_cols)):
                for j in range(i + 1, len(numeric_cols)):
                    col1 = numeric_cols[i]
                    col2 = numeric_cols[j]
                    engineered_df[f'{col1}_times_{col2}'] = engineered_df[col1] * engineered_df[col2]
        
        # 统计特征
        if 'age' in engineered_df.columns:
            engineered_df['age_group'] = pd.cut(
                engineered_df['age'], 
                bins=[0, 60, 70, 80, 90, 100], 
                labels=['<60', '60-69', '70-79', '80-89', '90+']
            )
        
        return engineered_df
    
    def evaluate_data_quality(self, df):
        """
        评估数据质量
        
        参数：
        - df: 待评估的DataFrame
        
        返回值：
        - dict: 数据质量报告
        """
        if df is None:
            return {}
        
        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': {},
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'numeric_stats': {}
        }
        
        # 计算每列的缺失值
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_percentage = (missing_count / len(df)) * 100
            quality_report['missing_values'][col] = {
                'count': int(missing_count),
                'percentage': round(missing_percentage, 2)
            }
        
        # 计算数值列的统计信息
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            quality_report['numeric_stats'][col] = {
                'mean': round(df[col].mean(), 2),
                'std': round(df[col].std(), 2),
                'min': round(df[col].min(), 2),
                'max': round(df[col].max(), 2),
                'median': round(df[col].median(), 2)
            }
        
        return quality_report
    
    def save_to_database(self, df, table_name):
        """
        保存数据到数据库
        
        参数：
        - df: 待保存的DataFrame
        - table_name: 表名
        
        返回值：
        - bool: 保存是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.commit()
            conn.close()
            print(f"数据成功保存到表 {table_name}")
            return True
        except Exception as e:
            print(f"保存数据到数据库失败: {e}")
            return False
    
    def process_data(self, data_source, source_type='database', config=None):
        """
        处理数据的主函数
        
        参数：
        - data_source: 数据来源（文件路径、API地址或SQL查询）
        - source_type: 数据源类型 ('database', 'csv', 'excel', 'api')
        - config: 处理配置
        
        返回值：
        - dict: 处理结果，包含处理后的数据和质量报告
        """
        # 加载数据
        if source_type == 'database':
            df = self.load_from_database(data_source)
        elif source_type == 'csv':
            df = self.load_from_csv(data_source)
        elif source_type == 'excel':
            df = self.load_from_excel(data_source)
        elif source_type == 'api':
            df = self.load_from_api(data_source)
        else:
            print(f"不支持的数据源类型: {source_type}")
            return None
        
        if df is None:
            return None
        
        # 评估原始数据质量
        original_quality = self.evaluate_data_quality(df)
        
        # 清洗数据
        cleaned_df = self.clean_data(df, config)
        
        # 特征工程
        engineered_df = self.feature_engineering(cleaned_df)
        
        # 评估处理后的数据质量
        processed_quality = self.evaluate_data_quality(engineered_df)
        
        return {
            'original_data': df,
            'cleaned_data': cleaned_df,
            'engineered_data': engineered_df,
            'original_quality': original_quality,
            'processed_quality': processed_quality
        }


# 全局数据处理器实例
data_processor = DataProcessor()


def process_data(data_source, source_type='database', config=None):
    """
    处理数据的便捷函数
    
    参数：
    - data_source: 数据来源
    - source_type: 数据源类型
    - config: 处理配置
    
    返回值：
    - dict: 处理结果
    """
    return data_processor.process_data(data_source, source_type, config)


def evaluate_data_quality(df):
    """
    评估数据质量的便捷函数
    
    参数：
    - df: 待评估的DataFrame
    
    返回值：
    - dict: 数据质量报告
    """
    return data_processor.evaluate_data_quality(df)


def save_to_database(df, table_name):
    """
    保存数据到数据库的便捷函数
    
    参数：
    - df: 待保存的DataFrame
    - table_name: 表名
    
    返回值：
    - bool: 保存是否成功
    """
    return data_processor.save_to_database(df, table_name)


if __name__ == '__main__':
    """当直接运行此文件时，测试数据处理功能"""
    # 测试从数据库加载数据
    query = 'SELECT * FROM health_record LIMIT 100'
    result = process_data(query, source_type='database')
    
    if result:
        print("\n原始数据质量报告:")
        print(json.dumps(result['original_quality'], ensure_ascii=False, indent=2))
        print("\n处理后数据质量报告:")
        print(json.dumps(result['processed_quality'], ensure_ascii=False, indent=2))
        print(f"\n处理前行数: {len(result['original_data'])}")
        print(f"处理后行数: {len(result['engineered_data'])}")
        print(f"处理后列数: {len(result['engineered_data'].columns)}")
