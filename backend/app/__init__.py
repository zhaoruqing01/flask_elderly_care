"""老年人护理需求预测系统 - 应用初始化

创建Flask应用实例并进行初始化配置
"""

from flask import Flask
import os

# 创建Flask应用实例
app = Flask(__name__)

# 配置应用
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DATABASE_PATH'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database', 'elderly_care.db')
app.config['MODEL_PATH'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'models')

# 确保模型目录存在
os.makedirs(app.config['MODEL_PATH'], exist_ok=True)

# 导入路由
from app.routes import health, service, prediction, admin, indicator
from app.routes.data_routes import bp as data_bp
from app.routes.chat_routes import bp as chat_bp

# 注册蓝图
app.register_blueprint(health.bp)
app.register_blueprint(service.bp)
app.register_blueprint(prediction.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(indicator.bp)
app.register_blueprint(data_bp)
app.register_blueprint(chat_bp)
