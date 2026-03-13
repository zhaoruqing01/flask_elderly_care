"""常见问题相关路由

提供常见问题列表的API接口
"""

from flask import Blueprint, jsonify

# 创建蓝图
bp = Blueprint('common', __name__, url_prefix='/api')

@bp.route('/common-questions', methods=['GET'])
def get_common_questions():
    """获取常见问题列表"""
    try:
        # 常见问题列表
        common_questions = [
            "某老人的最大需求是什么？",
            "如何提高老人的服务满意度？",
            "哪些社区的服务需求最高？",
            "老人的健康状况如何？",
            "如何优化服务资源配置？"
        ]
        return jsonify(common_questions)
    except Exception as e:
        print(f"获取常见问题失败: {e}")
        return jsonify({'error': '获取常见问题失败'}), 500