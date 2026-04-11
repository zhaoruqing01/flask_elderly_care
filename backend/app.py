"""flask_elderly_care 后端启动器

只从包中导入应用实例并运行，避免重复注册或冲突。
"""

from app import app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
