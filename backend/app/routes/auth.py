"""认证相关路由

提供登录、注册及角色权限验证API
"""

from flask import Blueprint, jsonify, request
from app.utils.database import db
import traceback

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    """登录接口"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
        result = db.execute(query, (username, password))
        
        if result:
            user = {
                'username': result[0][0],
                'role': result[0][1]
            }
            return jsonify({'message': '登录成功', 'user': user})
        else:
            return jsonify({'error': '用户名或密码错误'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/register', methods=['POST'])
def register():
    """注册接口"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'caregiver') # 默认注册为护工
        
        # 检查用户是否存在
        check_query = "SELECT id FROM users WHERE username = ?"
        if db.execute(check_query, (username,)):
            return jsonify({'error': '用户名已存在'}), 400
        
        insert_query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
        db.execute(insert_query, (username, password, role))
        
        return jsonify({'message': '注册成功', 'user': {'username': username, 'role': role}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/me', methods=['GET'])
def get_me():
    """获取当前用户信息"""
    # 这里暂时通过简单的参数模拟，实际应配合Token/Session
    username = request.args.get('username')
    if not username:
        return jsonify({'error': '未登录'}), 401
    
    query = "SELECT username, role FROM users WHERE username = ?"
    result = db.execute(query, (username,))
    if result:
        return jsonify({'user': {'username': result[0][0], 'role': result[0][1]}})
    return jsonify({'error': '用户不存在'}), 404
