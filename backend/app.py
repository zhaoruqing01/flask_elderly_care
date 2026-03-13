"""老年人护理需求预测系统 - 主入口文件

启动Flask应用的主入口
"""

import os
import sys

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    """应用入口
    
    当直接运行本文件时，启动Flask应用
    """
    # 启动应用，开启调试模式，端口为5008
    app.run(debug=True, port=5008)
