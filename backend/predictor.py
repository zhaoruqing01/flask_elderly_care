#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级预测模型模块

该模块用于训练和预测服务需求，包括：
1. 高级数据准备和特征工程
2. 多种模型训练和集成
3. 未来需求预测
4. 资源配置建议
5. 模型评估和监控

使用说明：
- 运行 train_model() 函数训练模型
- 运行 predict_demand() 函数预测需求
- 运行 get_resource_recommendations() 函数获取资源配置建议
"""

import sqlite3  # 用于操作 SQLite 数据库
import pandas as pd  # 用于数据处理
import numpy as np  # 用于数值计算
from datetime import datetime, timedelta  # 用于处理日期
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor  # 集成模型
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler  # 用于特征处理
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score  # 用于模型选择和评估
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, mean_absolute_percentage_error  # 模型评估指标
import joblib  # 用于保存和加载模型
import os  # 用于操作文件系统
import xgboost as xgb  # XGBoost模型
from sklearn.neural_network import MLPRegressor  # 神经网络模型

# 数据库文件路径
DB_PATH = 'database/elderly_care.db'
# 模型保存路径
MODEL_PATH = 'models/'

# 确保模型目录存在
os.makedirs(MODEL_PATH, exist_ok=True)

# 服务类型列表
SERVICE_TYPES = ['助餐', '助医', '保洁', '陪护', '康复']
# 社区列表
COMMUNITIES = ['社区A', '社区B', '社区C', '社区D', '社区E']


class AdvancedPredictor:
    """高级预测器类"""
    
    def __init__(self):
        """初始化预测器"""
        self.db_path = DB_PATH
        self.model_path = MODEL_PATH
        self.models = {}
        self.scalers = {}
        self.encoders = {}
    
    def prepare_training_data(self):
        """
        高级数据准备和特征工程
        
        功能：
        1. 从数据库读取服务记录
        2. 按日期、社区、服务类型分组计算需求量
        3. 提取丰富的特征：
           - 日期特征（星期几、月份、是否周末、季节等）
           - 滞后特征（前1天、前7天、前14天的需求）
           - 滚动特征（7天、14天移动平均和标准差）
           - 周期性特征（星期、月、季度的周期性）
        4. 编码类别特征（社区、服务类型）
        
        返回值：
        - X: 特征数据
        - y: 目标数据（需求量）
        - encoders: 编码器字典
        - feature_cols: 特征列名称列表
        """
        # 连接到数据库
        conn = sqlite3.connect(self.db_path)
        # 读取服务记录
        service_df = pd.read_sql('SELECT * FROM service_log', conn)
        # 读取老人信息，用于添加年龄相关特征
        senior_df = pd.read_sql('SELECT id, age FROM senior', conn)
        conn.close()
        
        # 检查数据是否为空
        if service_df.empty:
            return None, None, None, None
        
        # 将服务日期转换为日期类型
        service_df['service_date'] = pd.to_datetime(service_df['service_date'])
        
        # 合并老人信息
        service_df = pd.merge(service_df, senior_df, left_on='senior_id', right_on='id', how='left')
        
        # 按日期、社区、服务类型分组，计算每天的总服务时长（需求量）
        daily_service = service_df.groupby(['service_date', 'community_id', 'service_type']).agg(
            demand=('duration', 'sum'),
            avg_age=('age', 'mean'),
            satisfaction=('satisfaction', 'mean')
        ).reset_index()
        
        # 提取日期特征
        daily_service['day_of_week'] = daily_service['service_date'].dt.dayofweek  # 星期几（0-6）
        daily_service['day_of_month'] = daily_service['service_date'].dt.day  # 每月的第几天
        daily_service['month'] = daily_service['service_date'].dt.month  # 月份
        daily_service['is_weekend'] = (daily_service['day_of_week'] >= 5).astype(int)  # 是否周末（0或1）
        daily_service['week_of_year'] = daily_service['service_date'].dt.isocalendar().week.astype(int)  # 一年中的第几周
        daily_service['quarter'] = daily_service['service_date'].dt.quarter  # 季度
        
        # 季节特征
        def get_season(month):
            if month in [3, 4, 5]:
                return 0  # 春季
            elif month in [6, 7, 8]:
                return 1  # 夏季
            elif month in [9, 10, 11]:
                return 2  # 秋季
            else:
                return 3  # 冬季
        
        daily_service['season'] = daily_service['month'].apply(get_season)
        
        # 周期性特征（正弦和余弦变换）
        daily_service['day_of_week_sin'] = np.sin(2 * np.pi * daily_service['day_of_week'] / 7)
        daily_service['day_of_week_cos'] = np.cos(2 * np.pi * daily_service['day_of_week'] / 7)
        daily_service['month_sin'] = np.sin(2 * np.pi * daily_service['month'] / 12)
        daily_service['month_cos'] = np.cos(2 * np.pi * daily_service['month'] / 12)
        
        # 按社区和服务类型排序
        daily_service = daily_service.sort_values(['community_id', 'service_type', 'service_date'])
        
        # 计算滞后特征
        daily_service['demand_lag1'] = daily_service.groupby(['community_id', 'service_type'])['demand'].shift(1)  # 前1天的需求
        daily_service['demand_lag7'] = daily_service.groupby(['community_id', 'service_type'])['demand'].shift(7)  # 前7天的需求
        daily_service['demand_lag14'] = daily_service.groupby(['community_id', 'service_type'])['demand'].shift(14)  # 前14天的需求
        
        # 计算滚动特征
        daily_service['demand_rolling7_mean'] = daily_service.groupby(['community_id', 'service_type'])['demand'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )  # 7天移动平均需求
        daily_service['demand_rolling14_mean'] = daily_service.groupby(['community_id', 'service_type'])['demand'].transform(
            lambda x: x.rolling(window=14, min_periods=1).mean()
        )  # 14天移动平均需求
        daily_service['demand_rolling7_std'] = daily_service.groupby(['community_id', 'service_type'])['demand'].transform(
            lambda x: x.rolling(window=7, min_periods=1).std()
        )  # 7天移动标准差
        
        # 计算趋势特征
        def calculate_trend(y):
            try:
                return np.polyfit(range(len(y)), y, 1)[0]
            except np.linalg.LinAlgError:
                return 0
        
        daily_service['demand_trend'] = daily_service.groupby(['community_id', 'service_type'])['demand'].transform(
            lambda x: x.rolling(window=7, min_periods=1).apply(calculate_trend)
        )  # 7天趋势
        
        # 处理缺失值
        numeric_cols = daily_service.select_dtypes(include=[np.number]).columns
        daily_service[numeric_cols] = daily_service[numeric_cols].fillna(0)
        
        # 初始化编码器
        le_community = LabelEncoder()  # 社区编码器
        le_service = LabelEncoder()  # 服务类型编码器
        
        # 编码类别特征
        daily_service['community_encoded'] = le_community.fit_transform(daily_service['community_id'])
        daily_service['service_encoded'] = le_service.fit_transform(daily_service['service_type'])
        
        # 保存编码器
        joblib.dump(le_community, os.path.join(self.model_path, 'le_community.joblib'))
        joblib.dump(le_service, os.path.join(self.model_path, 'le_service.joblib'))
        
        # 特征列列表
        feature_cols = [
            'day_of_week', 'day_of_month', 'month', 'is_weekend', 
            'week_of_year', 'quarter', 'season',
            'day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos',
            'community_encoded', 'service_encoded',
            'avg_age', 'satisfaction',
            'demand_lag1', 'demand_lag7', 'demand_lag14',
            'demand_rolling7_mean', 'demand_rolling14_mean', 'demand_rolling7_std',
            'demand_trend'
        ]
        
        # 提取特征和目标
        X = daily_service[feature_cols]
        y = daily_service['demand']
        
        # 标准化数值特征
        scaler = StandardScaler()
        numeric_features = [col for col in feature_cols if col not in ['community_encoded', 'service_encoded', 'is_weekend', 'season']]
        X[numeric_features] = scaler.fit_transform(X[numeric_features])
        joblib.dump(scaler, os.path.join(self.model_path, 'scaler.joblib'))
        
        # 编码器字典
        encoders = {
            'le_community': le_community,
            'le_service': le_service,
            'scaler': scaler
        }
        
        return X, y, encoders, feature_cols
    
    def train_model(self):
        """
        训练高级预测模型
        
        功能：
        1. 准备训练数据
        2. 分割训练测试集
        3. 训练多种模型并进行集成
        4. 评估模型性能
        5. 保存模型和评估指标
        
        返回值：
        - model: 训练好的模型
        - metrics: 模型评估指标
        """
        # 准备训练数据
        X, y, encoders, feature_cols = self.prepare_training_data()
        
        # 检查数据是否足够
        if X is None or len(X) < 10:
            metrics = {
                'r2_score': 0,
                'mae': 0,
                'rmse': 0,
                'mape': 0,
                'train_samples': 0,
                'test_samples': 0,
                'trained_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': '数据不足，无法训练模型'
            }
            return None, metrics
        
        # 分割训练测试集（80%训练，20%测试）
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练多种模型
        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=200,  # 决策树数量
                max_depth=15,  # 树的最大深度
                min_samples_split=4,  # 节点分裂的最小样本数
                min_samples_leaf=2,  # 叶子节点的最小样本数
                max_features='sqrt',  # 每棵树考虑的特征数
                random_state=42,  # 随机种子
                n_jobs=-1  # 并行运行的任务数
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=150,  # 迭代次数
                learning_rate=0.1,  # 学习率
                max_depth=8,  # 树的最大深度
                min_samples_split=4,  # 节点分裂的最小样本数
                min_samples_leaf=2,  # 叶子节点的最小样本数
                random_state=42  # 随机种子
            ),
            'xgboost': xgb.XGBRegressor(
                n_estimators=150,  # 迭代次数
                learning_rate=0.1,  # 学习率
                max_depth=8,  # 树的最大深度
                subsample=0.8,  # 采样率
                colsample_bytree=0.8,  # 特征采样率
                random_state=42  # 随机种子
            ),
            'mlp': MLPRegressor(
                hidden_layer_sizes=(128, 64, 32),  # 隐藏层大小
                activation='relu',  # 激活函数
                solver='adam',  # 优化器
                max_iter=500,  # 最大迭代次数
                random_state=42  # 随机种子
            )
        }
        
        # 训练每个模型
        trained_models = {}
        for name, model in models.items():
            print(f"训练 {name} 模型...")
            model.fit(X_train, y_train)
            trained_models[name] = model
        
        # 创建集成模型
        ensemble_model = VotingRegressor(
            estimators=[(name, model) for name, model in trained_models.items()],
            weights=[0.3, 0.25, 0.3, 0.15]  # 权重分配
        )
        
        print("训练集成模型...")
        ensemble_model.fit(X_train, y_train)
        
        # 预测测试集
        y_pred = ensemble_model.predict(X_test)
        
        # 计算评估指标
        metrics = {
            'r2_score': round(r2_score(y_test, y_pred), 4),  # R²评分
            'mae': round(mean_absolute_error(y_test, y_pred), 2),  # 平均绝对误差
            'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),  # 均方根误差
            'mape': round(mean_absolute_percentage_error(y_test, y_pred), 4),  # 平均绝对百分比误差
            'train_samples': len(X_train),  # 训练样本数
            'test_samples': len(X_test),  # 测试样本数
            'trained_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 训练时间
        }
        
        # 交叉验证
        cv_scores = cross_val_score(ensemble_model, X, y, cv=5, scoring='r2')
        metrics['cv_mean_r2'] = round(cv_scores.mean(), 4)
        metrics['cv_std_r2'] = round(cv_scores.std(), 4)
        
        # 保存模型和评估指标
        joblib.dump(ensemble_model, os.path.join(self.model_path, 'demand_prediction_model.joblib'))
        joblib.dump(trained_models, os.path.join(self.model_path, 'individual_models.joblib'))
        joblib.dump(metrics, os.path.join(self.model_path, 'model_metrics.joblib'))
        joblib.dump(feature_cols, os.path.join(self.model_path, 'feature_cols.joblib'))
        
        return ensemble_model, metrics
    
    def load_model(self):
        """
        加载已训练的模型
        
        返回值：
        - 训练好的模型或None（如果模型不存在）
        """
        model_path = os.path.join(self.model_path, 'demand_prediction_model.joblib')
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None
    
    def get_model_metrics(self):
        """
        获取模型评估指标
        
        返回值：
        - 模型评估指标
        """
        metrics_path = os.path.join(self.model_path, 'model_metrics.joblib')
        if os.path.exists(metrics_path):
            return joblib.load(metrics_path)
        # 模型未训练时返回默认值
        return {
            'r2_score': 0,
            'mae': 0,
            'rmse': 0,
            'mape': 0,
            'train_samples': 0,
            'test_samples': 0,
            'cv_mean_r2': 0,
            'cv_std_r2': 0,
            'trained_at': '-',
            'error': '模型未训练'
        }
    
    def predict_demand(self, community_id, service_type, days=30):
        """
        预测未来服务需求量
        
        参数：
        - community_id: 社区ID
        - service_type: 服务类型
        - days: 预测天数
        
        返回值：
        - 预测结果列表，每个元素包含日期、社区、服务类型、预测需求量
        """
        # 加载模型
        model = self.load_model()
        if model is None:
            return []
        
        try:
            # 加载编码器、缩放器和特征列
            le_community = joblib.load(os.path.join(self.model_path, 'le_community.joblib'))
            le_service = joblib.load(os.path.join(self.model_path, 'le_service.joblib'))
            scaler = joblib.load(os.path.join(self.model_path, 'scaler.joblib'))
            feature_cols = joblib.load(os.path.join(self.model_path, 'feature_cols.joblib'))
        except:
            return []
        
        # 连接到数据库
        conn = sqlite3.connect(self.db_path)
        # 查询历史服务记录
        query = f"""
        SELECT service_date, SUM(duration) as demand, AVG(age) as avg_age, AVG(satisfaction) as satisfaction
        FROM service_log 
        JOIN senior ON service_log.senior_id = senior.id
        WHERE community_id = '{community_id}' AND service_type = '{service_type}'
        GROUP BY service_date
        ORDER BY service_date DESC
        LIMIT 30
        """
        history_df = pd.read_sql(query, conn)
        conn.close()
        
        # 计算初始特征值
        if not history_df.empty:
            history_df['service_date'] = pd.to_datetime(history_df['service_date'])
            history_df = history_df.sort_values('service_date')
            recent_demand = history_df['demand'].tolist()
            recent_age = history_df['avg_age'].tolist()
            recent_satisfaction = history_df['satisfaction'].tolist()
            
            demand_lag1 = recent_demand[-1] if len(recent_demand) > 0 else 0
            demand_lag7 = recent_demand[-7] if len(recent_demand) >= 7 else demand_lag1
            demand_lag14 = recent_demand[-14] if len(recent_demand) >= 14 else demand_lag1
            demand_rolling7_mean = np.mean(recent_demand[-7:]) if len(recent_demand) >= 7 else np.mean(recent_demand) if recent_demand else 0
            demand_rolling14_mean = np.mean(recent_demand[-14:]) if len(recent_demand) >= 14 else demand_rolling7_mean
            demand_rolling7_std = np.std(recent_demand[-7:]) if len(recent_demand) >= 7 else 0
            try:
                demand_trend = np.polyfit(range(min(7, len(recent_demand))), recent_demand[-min(7, len(recent_demand)):], 1)[0] if recent_demand else 0
            except np.linalg.LinAlgError:
                demand_trend = 0
            avg_age = np.mean(recent_age) if recent_age else 75
            satisfaction = np.mean(recent_satisfaction) if recent_satisfaction else 4.0
        else:
            # 无历史数据时使用默认值
            demand_lag1 = 100
            demand_lag7 = 100
            demand_lag14 = 100
            demand_rolling7_mean = 100
            demand_rolling14_mean = 100
            demand_rolling7_std = 20
            demand_trend = 0
            avg_age = 75
            satisfaction = 4.0
        
        # 生成未来日期
        future_dates = []
        start_date = datetime.now()
        for i in range(1, days + 1):
            future_date = start_date + timedelta(days=i)
            future_dates.append(future_date)
        
        # 存储预测结果
        predictions = []
        prev_predictions = []  # 存储之前的预测结果，用于计算滞后特征
        
        # 逐天预测
        for date in future_dates:
            # 提取日期特征
            day_of_week = date.weekday()
            day_of_month = date.day
            month = date.month
            is_weekend = 1 if day_of_week >= 5 else 0
            week_of_year = date.isocalendar().week
            quarter = (month - 1) // 3 + 1
            
            # 季节特征
            season = get_season(month)
            
            # 周期性特征
            day_of_week_sin = np.sin(2 * np.pi * day_of_week / 7)
            day_of_week_cos = np.cos(2 * np.pi * day_of_week / 7)
            month_sin = np.sin(2 * np.pi * month / 12)
            month_cos = np.cos(2 * np.pi * month / 12)
            
            # 编码类别特征
            try:
                community_encoded = le_community.transform([community_id])[0]
            except:
                community_encoded = 0
            
            try:
                service_encoded = le_service.transform([service_type])[0]
            except:
                service_encoded = 0
            
            # 更新滞后特征（使用之前的预测结果）
            if len(prev_predictions) >= 1:
                demand_lag1 = prev_predictions[-1]
            if len(prev_predictions) >= 7:
                demand_lag7 = prev_predictions[-7]
            if len(prev_predictions) >= 14:
                demand_lag14 = prev_predictions[-14]
            if len(prev_predictions) > 0:
                demand_rolling7_mean = np.mean(prev_predictions[-7:])
                demand_rolling14_mean = np.mean(prev_predictions[-14:])
                demand_rolling7_std = np.std(prev_predictions[-7:]) if len(prev_predictions) >= 7 else 20
                if len(prev_predictions) >= 2:
                    try:
                        demand_trend = np.polyfit(range(min(7, len(prev_predictions))), prev_predictions[-min(7, len(prev_predictions)):], 1)[0]
                    except np.linalg.LinAlgError:
                        demand_trend = 0
            
            # 构建特征
            features = pd.DataFrame([[
                day_of_week, day_of_month, month, is_weekend, 
                week_of_year, quarter, season,
                day_of_week_sin, day_of_week_cos, month_sin, month_cos,
                community_encoded, service_encoded,
                avg_age, satisfaction,
                demand_lag1, demand_lag7, demand_lag14,
                demand_rolling7_mean, demand_rolling14_mean, demand_rolling7_std,
                demand_trend
            ]], columns=feature_cols)
            
            # 标准化数值特征
            numeric_features = [col for col in feature_cols if col not in ['community_encoded', 'service_encoded', 'is_weekend', 'season']]
            features[numeric_features] = scaler.transform(features[numeric_features])
            
            # 预测需求量
            predicted_demand = model.predict(features)[0]
            predicted_demand = max(0, predicted_demand)  # 确保预测值非负
            prev_predictions.append(predicted_demand)
            
            # 添加预测结果
            predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'community_id': community_id,
                'service_type': service_type,
                'predicted_demand': round(predicted_demand, 1)
            })
        
        return predictions
    
    def get_prediction_trend(self, community_id='社区A', service_type='助餐', days=7):
        """
        获取预测趋势数据
        
        参数：
        - community_id: 社区ID
        - service_type: 服务类型
        - days: 预测天数
        
        返回值：
        - 包含历史数据和预测数据的字典
        """
        # 连接到数据库
        conn = sqlite3.connect(self.db_path)
        # 查询历史服务记录
        query = f"""
        SELECT service_date, SUM(duration) as demand 
        FROM service_log 
        WHERE community_id = '{community_id}' AND service_type = '{service_type}'
        GROUP BY service_date
        ORDER BY service_date DESC
        LIMIT 14
        """
        history_df = pd.read_sql(query, conn)
        conn.close()
        
        # 处理历史数据
        historical = {
            'dates': [],
            'values': []
        }
        
        if not history_df.empty:
            history_df['service_date'] = pd.to_datetime(history_df['service_date'])
            history_df = history_df.sort_values('service_date')
            historical['dates'] = history_df['service_date'].dt.strftime('%Y-%m-%d').tolist()
            historical['values'] = history_df['demand'].tolist()
        
        # 获取预测数据
        predictions = self.predict_demand(community_id, service_type, days)
        
        # 处理预测数据
        predicted = {
            'dates': [p['date'] for p in predictions] if predictions else [],
            'values': [p['predicted_demand'] for p in predictions] if predictions else []
        }
        
        return {
            'historical': historical,
            'predicted': predicted
        }
    
    def get_resource_recommendations(self):
        """
        获取资源配置建议
        
        功能：
        1. 预测每个社区每种服务的未来7天需求
        2. 计算所需工作人员数量
        3. 按需求优先级排序
        4. 生成详细的资源配置方案
        
        返回值：
        - 资源配置建议列表
        """
        all_predictions = []
        
        # 预测每个社区每种服务的需求
        for community in COMMUNITIES:
            for service in SERVICE_TYPES:
                preds = self.predict_demand(community, service, days=7)
                if preds:
                    # 计算7天总需求
                    total_demand = sum(p['predicted_demand'] for p in preds)
                    daily_avg = total_demand / 7
                    
                    # 计算需求波动
                    demands = [p['predicted_demand'] for p in preds]
                    demand_std = np.std(demands) if len(demands) > 1 else 0
                    demand_trend = np.polyfit(range(len(demands)), demands, 1)[0] if len(demands) > 1 else 0
                    
                    all_predictions.append({
                        'community': community,
                        'service': service,
                        'total_demand': total_demand,
                        'daily_avg': daily_avg,
                        'demand_std': demand_std,
                        'demand_trend': demand_trend
                    })
        
        if not all_predictions:
            return []
        
        # 生成资源配置建议
        recommendations = []
        # 按总需求降序排序，取前15个
        for pred in sorted(all_predictions, key=lambda x: x['total_demand'], reverse=True)[:15]:
            # 计算所需工作人员数量（假设每人每天工作60分钟）
            base_staff = max(1, int(pred['daily_avg'] / 60))
            # 根据需求波动和趋势调整
            adjustment_factor = 1.0
            if pred['demand_std'] > 30:
                adjustment_factor = 1.2  # 需求波动大，增加人员
            if pred['demand_trend'] > 5:
                adjustment_factor *= 1.1  # 需求上升趋势，增加人员
            
            staff_needed = max(1, int(base_staff * adjustment_factor))
            
            # 计算优先级
            if pred['total_demand'] > 500:
                priority = '高'
            elif pred['total_demand'] > 200:
                priority = '中'
            else:
                priority = '低'
            
            # 生成详细建议
            recommendation = {
                'community': pred['community'],
                'service': pred['service'],
                'predicted_demand': round(pred['total_demand'], 1),
                'daily_avg': round(pred['daily_avg'], 1),
                'demand_std': round(pred['demand_std'], 1),
                'demand_trend': round(pred['demand_trend'], 2),
                'staff_needed': staff_needed,
                'priority': priority,
                'suggestion': self._generate_suggestion(pred)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_suggestion(self, pred):
        """
        生成资源配置建议文本
        
        参数：
        - pred: 预测结果字典
        
        返回值：
        - str: 建议文本
        """
        suggestions = []
        
        if pred['priority'] == '高':
            suggestions.append('建议立即增加人员配置，确保服务质量')
        elif pred['priority'] == '中':
            suggestions.append('建议适当增加人员，密切关注需求变化')
        else:
            suggestions.append('建议保持现有人员配置，定期监测需求')
        
        if pred['demand_trend'] > 5:
            suggestions.append('需求呈上升趋势，建议提前做好人员储备')
        elif pred['demand_trend'] < -5:
            suggestions.append('需求呈下降趋势，可以考虑适当减少人员')
        
        if pred['demand_std'] > 30:
            suggestions.append('需求波动较大，建议配备灵活的临时人员')
        
        return ' '.join(suggestions)


# 季节函数
def get_season(month):
    if month in [3, 4, 5]:
        return 0  # 春季
    elif month in [6, 7, 8]:
        return 1  # 夏季
    elif month in [9, 10, 11]:
        return 2  # 秋季
    else:
        return 3  # 冬季


# 全局预测器实例
advanced_predictor = AdvancedPredictor()


def train_model():
    """
    训练模型的便捷函数
    
    返回值：
    - model: 训练好的模型
    - metrics: 模型评估指标
    """
    return advanced_predictor.train_model()


def load_model():
    """
    加载模型的便捷函数
    
    返回值：
    - 训练好的模型或None
    """
    return advanced_predictor.load_model()


def get_model_metrics():
    """
    获取模型评估指标的便捷函数
    
    返回值：
    - 模型评估指标
    """
    return advanced_predictor.get_model_metrics()


def predict_demand(community_id, service_type, days=30):
    """
    预测需求的便捷函数
    
    参数：
    - community_id: 社区ID
    - service_type: 服务类型
    - days: 预测天数
    
    返回值：
    - 预测结果列表
    """
    return advanced_predictor.predict_demand(community_id, service_type, days)


def get_prediction_trend(community_id='社区A', service_type='助餐', days=7):
    """
    获取预测趋势的便捷函数
    
    参数：
    - community_id: 社区ID
    - service_type: 服务类型
    - days: 预测天数
    
    返回值：
    - 包含历史数据和预测数据的字典
    """
    return advanced_predictor.get_prediction_trend(community_id, service_type, days)


def get_resource_recommendations():
    """
    获取资源配置建议的便捷函数
    
    返回值：
    - 资源配置建议列表
    """
    return advanced_predictor.get_resource_recommendations()


if __name__ == '__main__':
    """当直接运行此文件时，测试预测功能"""
    print("训练模型...")
    model, metrics = train_model()
    print("模型评估指标:")
    print(metrics)
    
    print("\n预测需求...")
    predictions = predict_demand('社区A', '助餐', days=7)
    print(f"预测了 {len(predictions)} 天的需求")
    print("前3天的预测结果:")
    for pred in predictions[:3]:
        print(pred)
    
    print("\n获取资源配置建议...")
    recommendations = get_resource_recommendations()
    print(f"生成了 {len(recommendations)} 条资源配置建议")
    print("前3条建议:")
    for rec in recommendations[:3]:
        print(rec)
