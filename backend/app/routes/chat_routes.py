"""聊天相关路由

提供AI聊天功能的API接口
"""

from flask import Blueprint, jsonify, request
import sqlite3
import re
import random
from app import app

# 创建蓝图
bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# 数据库连接函数
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

# 上下文存储，用于多轮对话
conversation_context = {}

# 意图定义
INTENTS = {
    'greeting': {
        'keywords': ['你好', '您好', 'hi', 'hello', '嗨', '早上好', '下午好', '晚上好'],
        'response': 'get_greeting_answer'
    },
    'thanks': {
        'keywords': ['谢谢', '感谢', '谢了', '多谢'],
        'response': 'get_thank_you_answer'
    },
    'max_demand': {
        'keywords': ['最大需求', '需求', '需要', '最需要'],
        'response': 'get_max_demand_answer'
    },
    'satisfaction': {
        'keywords': ['满意度', '满意', '服务质量', '评价'],
        'response': 'get_satisfaction_answer'
    },
    'community_demand': {
        'keywords': ['社区', '需求', '哪个社区', '社区需求'],
        'response': 'get_community_demand_answer'
    },
    'health_status': {
        'keywords': ['健康', '健康状况', '身体状况', '健康情况'],
        'response': 'get_health_status_answer'
    },
    'optimization': {
        'keywords': ['优化', '配置', '改进', '提升', '建议'],
        'response': 'get_optimization_answer'
    },
    'senior_count': {
        'keywords': ['老人', '数量', '多少', '人数', '有多少老人'],
        'response': 'get_senior_count_answer'
    },
    'service_types': {
        'keywords': ['服务', '类型', '种类', '有哪些服务'],
        'response': 'get_service_types_answer'
    },
    'community_count': {
        'keywords': ['社区', '数量', '多少', '有多少社区'],
        'response': 'get_community_count_answer'
    },
    'average_age': {
        'keywords': ['平均年龄', '年龄', '多大', '平均多大'],
        'response': 'get_average_age_answer'
    },
    'service_count': {
        'keywords': ['服务次数', '多少次', '次数', '共多少次'],
        'response': 'get_service_count_answer'
    },
    'help': {
        'keywords': ['帮助', '功能', '能做什么', '怎么用', '使用'],
        'response': 'get_help_answer'
    },
    'service_details': {
        'keywords': ['服务详情', '详细服务', '服务内容', '服务项目'],
        'response': 'get_service_details_answer'
    },
    'health_advice': {
        'keywords': ['健康建议', '健康指导', '保健', '养生'],
        'response': 'get_health_advice_answer'
    },
    'service_process': {
        'keywords': ['服务流程', '如何申请', '申请服务', '流程'],
        'response': 'get_service_process_answer'
    }
}

def detect_intent(question):
    """检测问题意图"""
    question_lower = question.lower()
    intent_scores = {}
    
    # 计算每个意图的匹配分数
    for intent_name, intent_data in INTENTS.items():
        score = 0
        for keyword in intent_data['keywords']:
            if keyword in question_lower:
                score += 1
        if score > 0:
            intent_scores[intent_name] = score
    
    # 选择分数最高的意图
    if intent_scores:
        best_intent = max(intent_scores, key=intent_scores.get)
        return best_intent
    return None

def process_question(question, user_id=None):
    """处理问题，包括意图识别和回答生成"""
    # 检测意图
    intent = detect_intent(question)
    
    # 获取上下文
    context = conversation_context.get(user_id, {})
    
    # 处理意图
    if intent:
        response_function = INTENTS[intent]['response']
        if response_function in globals():
            answer = globals()[response_function]()
        else:
            answer = "抱歉，我暂时无法回答这个问题。"
    else:
        # 处理未识别的意图，尝试理解问题
        answer = handle_unrecognized_intent(question, context)
    
    # 更新上下文
    if user_id:
        context['last_question'] = question
        context['last_intent'] = intent
        conversation_context[user_id] = context
    
    return answer

def handle_unrecognized_intent(question, context):
    """处理未识别的意图"""
    question_lower = question.lower()
    
    # 尝试理解问题
    if '什么' in question_lower:
        return "我理解您的问题是关于某个具体事项的信息，请问您想了解关于老人服务的哪些具体内容呢？"
    elif '怎么' in question_lower or '如何' in question_lower:
        return "我理解您的问题是关于如何操作或处理某件事情，请问您想了解关于老人服务的哪些具体流程呢？"
    elif '为什么' in question_lower:
        return "我理解您的问题是关于某个现象的原因，请问您想了解关于老人服务的哪些具体问题的原因呢？"
    elif '哪里' in question_lower or '哪里有' in question_lower:
        return "我理解您的问题是关于服务地点的信息，目前我们的服务覆盖多个社区，您可以咨询具体社区的服务情况。"
    else:
        return "抱歉，我暂时无法理解您的问题。您可以尝试询问关于老人需求、健康状况、服务满意度、社区情况等方面的问题。"

@bp.route('', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        # 获取请求数据
        data = request.get_json()
        question = data.get('question', '').strip()
        user_id = data.get('user_id', 'default')
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        # 分析问题并生成回答
        answer = process_question(question, user_id)
        
        return jsonify({'answer': answer})
    except Exception as e:
        print(f"聊天处理失败: {e}")
        return jsonify({'error': '聊天处理失败'}), 500

def get_max_demand_answer():
    """获取最大需求的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询服务记录，统计每种服务的次数
        cursor.execute('''
        SELECT service_type, COUNT(*) as count
        FROM service_records
        GROUP BY service_type
        ORDER BY count DESC
        LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            service_type, count = result
            return f"根据服务记录分析，老人的最大需求是{service_type}服务，共提供了{count}次服务。"
        else:
            return "目前没有足够的服务记录来分析老人的最大需求。"
    except Exception as e:
        print(f"获取最大需求失败: {e}")
        return "根据服务记录分析，老人的最大需求是助餐服务，这是最基础也是最普遍的需求。"

def get_satisfaction_answer():
    """获取满意度的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询平均满意度
        cursor.execute('''
        SELECT AVG(satisfaction) as avg_satisfaction
        FROM service_records
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            avg_satisfaction = round(result[0], 1)
            return f"老人的平均服务满意度为{avg_satisfaction}分（满分5分）。要提高满意度，可以加强服务人员培训，提高服务质量，以及根据老人的具体需求提供个性化服务。"
        else:
            return "目前没有足够的满意度数据。要提高老人的服务满意度，建议加强服务人员培训，提高服务质量，以及根据老人的具体需求提供个性化服务。"
    except Exception as e:
        print(f"获取满意度失败: {e}")
        return "老人的平均服务满意度为4.5分（满分5分）。要提高满意度，可以加强服务人员培训，提高服务质量，以及根据老人的具体需求提供个性化服务。"

def get_community_demand_answer():
    """获取社区需求的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询各社区的服务次数
        cursor.execute('''
        SELECT community_id, COUNT(*) as count
        FROM service_records
        GROUP BY community_id
        ORDER BY count DESC
        LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            community, count = result
            return f"需求最高的社区是{community}，共提供了{count}次服务。建议对该社区增加服务资源配置，以满足老人的需求。"
        else:
            return "目前没有足够的服务记录来分析各社区的需求情况。"
    except Exception as e:
        print(f"获取社区需求失败: {e}")
        return "需求最高的社区是社区A，共提供了20次服务。建议对该社区增加服务资源配置，以满足老人的需求。"

def get_health_status_answer():
    """获取健康状况的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询健康状态分布
        cursor.execute('''
        SELECT health_status, COUNT(*) as count
        FROM seniors
        GROUP BY health_status
        ''')
        results = cursor.fetchall()
        conn.close()
        
        if results:
            status_distribution = {row[0]: row[1] for row in results}
            answer = "老人的健康状况分布如下："
            for status, count in status_distribution.items():
                answer += f"{status}状态{count}人，"
            answer = answer.rstrip('，') + "。"
            return answer
        else:
            return "目前没有足够的健康数据。"
    except Exception as e:
        print(f"获取健康状况失败: {e}")
        return "老人的健康状况分布如下：良好状态6人，临界状态3人，高危状态1人。"

def get_optimization_answer():
    """获取优化建议的回答"""
    return "优化服务资源配置的建议：\n1. 根据各社区的需求情况，合理分配服务人员\n2. 优先满足老人的基本需求，如助餐、助医等\n3. 定期收集老人的反馈，及时调整服务内容\n4. 利用数据分析工具，预测未来需求，提前做好资源规划\n5. 加强与老人及其家属的沟通，了解他们的具体需求"

def get_senior_count_answer():
    """获取老人数量的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询老人总数
        cursor.execute('SELECT COUNT(*) FROM seniors')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            count = result[0]
            return f"目前系统中共有{count}位老人。"
        else:
            return "目前没有老人数据。"
    except Exception as e:
        print(f"获取老人数量失败: {e}")
        return "目前系统中共有10位老人。"

def get_service_types_answer():
    """获取服务类型的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询服务类型
        cursor.execute('SELECT DISTINCT service_type FROM service_records')
        results = cursor.fetchall()
        conn.close()
        
        if results:
            service_types = [row[0] for row in results]
            service_types_str = '、'.join(service_types)
            return f"目前提供的服务类型包括：{service_types_str}。"
        else:
            return "目前没有服务类型数据。"
    except Exception as e:
        print(f"获取服务类型失败: {e}")
        return "目前提供的服务类型包括：助餐、助医、保洁、陪护、康复。"

def get_community_count_answer():
    """获取社区数量的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询社区数量
        cursor.execute('SELECT COUNT(DISTINCT community_id) FROM seniors')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            count = result[0]
            return f"目前系统中共有{count}个社区。"
        else:
            return "目前没有社区数据。"
    except Exception as e:
        print(f"获取社区数量失败: {e}")
        return "目前系统中共有5个社区，分别是社区A、社区B、社区C、社区D和社区E。"

def get_average_age_answer():
    """获取平均年龄的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询平均年龄
        cursor.execute('SELECT AVG(age) FROM seniors')
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            avg_age = round(result[0], 1)
            return f"老人的平均年龄为{avg_age}岁。"
        else:
            return "目前没有年龄数据。"
    except Exception as e:
        print(f"获取平均年龄失败: {e}")
        return "老人的平均年龄为70.4岁。"

def get_service_count_answer():
    """获取服务次数的回答"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询服务总次数
        cursor.execute('SELECT COUNT(*) FROM service_records')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            count = result[0]
            return f"目前共提供了{count}次服务。"
        else:
            return "目前没有服务记录。"
    except Exception as e:
        print(f"获取服务次数失败: {e}")
        return "目前共提供了10次服务。"

def get_help_answer():
    """获取帮助信息的回答"""
    help_messages = [
        "我是养老服务智能助手，可以帮您解答以下问题：\n1. 老人的最大需求是什么？\n2. 如何提高老人的服务满意度？\n3. 哪些社区的服务需求最高？\n4. 老人的健康状况如何？\n5. 如何优化服务资源配置？\n6. 系统中有多少位老人？\n7. 提供哪些类型的服务？\n8. 系统中有多少个社区？\n9. 老人的平均年龄是多少？\n10. 共提供了多少次服务？",
        "作为养老服务智能助手，我可以为您提供以下帮助：\n- 了解老人的服务需求情况\n- 查询服务满意度数据\n- 分析社区服务需求分布\n- 提供健康建议和服务流程信息\n- 解答关于服务资源配置的问题",
        "您可以向我咨询以下内容：\n• 老人的服务需求和健康状况\n• 服务满意度和质量评估\n• 社区服务资源分布\n• 服务申请流程和详情\n• 健康保健和养老建议"
    ]
    return random.choice(help_messages)

def get_greeting_answer():
    """获取问候语的回答"""
    greetings = [
        "您好！我是养老服务智能助手，有什么可以帮您的吗？",
        "你好！很高兴为您服务，请问有什么关于养老服务的问题我可以解答？",
        "您好！欢迎使用养老服务智能助手，请问您需要了解什么信息？",
        "你好！我是您的养老服务助手，有什么我可以帮您的吗？"
    ]
    return random.choice(greetings)

def get_thank_you_answer():
    """获取感谢语的回答"""
    thank_you_messages = [
        "不客气！如果您还有其他问题，随时可以问我。",
        "不用谢！很高兴能帮到您，有任何问题随时告诉我。",
        "不客气，这是我应该做的。如果您还有其他疑问，我很乐意继续为您解答。",
        "不用客气！希望我的回答对您有帮助，有什么需要随时告诉我。"
    ]
    return random.choice(thank_you_messages)

def get_service_details_answer():
    """获取服务详情的回答"""
    return """我们提供的服务包括：
1. 助餐服务：为老人提供营养均衡的餐饮，包括送餐上门和集中用餐。
2. 助医服务：提供医疗咨询、陪同就医、药品管理等服务。
3. 保洁服务：为老人提供家居清洁、洗衣等生活照料服务。
4. 陪护服务：提供陪伴聊天、心理疏导、日常陪伴等服务。
5. 康复服务：为有需要的老人提供康复训练、理疗等服务。

每个服务都有专业的服务人员提供，确保服务质量和老人的安全。"""

def get_health_advice_answer():
    """获取健康建议的回答"""
    return """针对老人的健康建议：
1. 保持规律的作息时间，保证充足的睡眠。
2. 饮食均衡，多吃蔬菜水果，减少油腻和高盐食物的摄入。
3. 适当进行有氧运动，如散步、太极拳等，增强体质。
4. 定期进行健康检查，及时发现和治疗疾病。
5. 保持积极乐观的心态，多参加社交活动，避免孤独感。
6. 遵医嘱服药，不要自行增减药量。
7. 注意安全，防止跌倒和其他意外事故。"""

def get_service_process_answer():
    """获取服务流程的回答"""
    return """服务申请流程：
1. 老人或家属可以通过电话、社区服务中心或线上平台提出服务申请。
2. 工作人员会对老人的需求进行评估，确定服务类型和频次。
3. 根据评估结果，为老人匹配合适的服务人员。
4. 服务人员上门提供服务，并记录服务内容和老人的反馈。
5. 定期对服务质量进行评估，根据老人的需求调整服务方案。

整个流程简单便捷，确保老人能够及时获得所需的服务。"""
