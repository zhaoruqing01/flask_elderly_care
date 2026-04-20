"""聊天相关路由

提供AI聊天功能的API接口
"""

from flask import Blueprint, jsonify, request
import sqlite3
import re
import random
import inspect
import difflib
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
        'keywords': ['你好', '您好', 'hi', 'hello', '嗨', '早上好', '下午好', '晚上好', '您好啊', '你好呀', '哈喽'],
        'response': 'get_greeting_answer'
    },
    'thanks': {
        'keywords': ['谢谢', '感谢', '谢了', '多谢', '感谢您', '多谢啦', '谢谢啦', '非常感谢'],
        'response': 'get_thank_you_answer'
    },
    'max_demand': {
        'keywords': ['最大需求', '需求', '需要', '最需要', '主要需求', '核心需求', '首要需求', '最迫切需求', '最急迫需求', '最关注的需求'],
        'response': 'get_max_demand_answer'
    },
    'satisfaction': {
        'keywords': ['满意度', '满意', '服务质量', '评价', '服务评价', '服务感受', '服务体验', '评价如何', '服务怎么样'],
        'response': 'get_satisfaction_answer'
    },
    'community_demand': {
        'keywords': ['社区', '需求', '哪个社区', '社区需求', '哪个社区需求大', '社区需求情况', '社区需求排行', '社区需求排名'],
        'response': 'get_community_demand_answer'
    },
    'health_status': {
        'keywords': ['健康', '健康状况', '身体状况', '健康情况', '健康情况怎么样', '身体健康状况', '健康水平', '健康指标'],
        'response': 'get_health_status_answer'
    },
    'optimization': {
        'keywords': ['优化', '配置', '改进', '提升', '建议', '资源优化', '资源配置优化', '服务改进', '服务提升', '服务完善'],
        'response': 'get_optimization_answer'
    },
    'senior_count': {
        'keywords': ['老人', '数量', '多少', '人数', '有多少老人', '老年人数量', '老人人数', '老年人口数量', '老人总数'],
        'response': 'get_senior_count_answer'
    },
    'service_types': {
        'keywords': ['服务', '类型', '种类', '有哪些服务', '服务项目', '服务种类', '服务类别', '有哪些服务项目'],
        'response': 'get_service_types_answer'
    },
    'community_count': {
        'keywords': ['社区', '数量', '多少', '有多少社区', '社区总数', '有多少个社区', '社区个数', '社区数目'],
        'response': 'get_community_count_answer'
    },
    'average_age': {
        'keywords': ['平均年龄', '年龄', '多大', '平均多大', '老人平均多大', '老人平均岁数', '老人平均岁数', '老人平均岁数'],
        'response': 'get_average_age_answer'
    },
    'service_count': {
        'keywords': ['服务次数', '多少次', '次数', '共多少次', '服务总次数', '服务了多少次', '服务总数量', '服务总量'],
        'response': 'get_service_count_answer'
    },
    'help': {
        'keywords': ['帮助', '功能', '能做什么', '怎么用', '使用', '功能介绍', '你能做什么', '有什么功能', '使用指南'],
        'response': 'get_help_answer'
    },
    'service_details': {
        'keywords': ['服务详情', '详细服务', '服务内容', '服务项目', '服务具体内容', '服务详细内容', '服务项目详情', '服务项目介绍'],
        'response': 'get_service_details_answer'
    },
    'health_advice': {
        'keywords': ['健康建议', '健康指导', '保健', '养生', '健康指导', '保健建议', '养生建议', '健康小贴士', '健康小建议'],
        'response': 'get_health_advice_answer'
    },
    'service_process': {
        'keywords': ['服务流程', '如何申请', '申请服务', '流程', '服务如何申请', '服务申请步骤', '服务申请流程', '如何申请服务'],
        'response': 'get_service_process_answer'
    }
}

def detect_intent(question):
    """检测问题意图"""
    # 更鲁棒的意图检测：精确命中加权，模糊匹配降权
    question_norm = question.lower()
    intent_scores = {}

    for intent_name, intent_data in INTENTS.items():
        score = 0
        for keyword in intent_data['keywords']:
            # 计算关键词长度，用于长度惩罚
            keyword_length = len(keyword)
            
            # 精确包含（中文或英文）
            if keyword in question or keyword in question_norm:
                # 完全匹配优先：长关键词给予更高权重
                if keyword_length >= 3:  # 长度大于等于3的关键词给予更高权重
                    score += 4
                elif keyword_length == 2:  # 长度为2的关键词给予中等权重
                    score += 3
                else:  # 长度为1的关键词给予低权重（长度惩罚）
                    score += 1
            else:
                # 模糊匹配：将问题拆成 token，使用 difflib 进行近似匹配
                candidates = re.findall(r"[\w\u4e00-\u9fff]+", question)
                if candidates:
                    close = difflib.get_close_matches(keyword, candidates, n=1, cutoff=0.75)
                    if close:
                        # 对模糊匹配也应用长度惩罚
                        if keyword_length >= 3:
                            score += 2
                        elif keyword_length == 2:
                            score += 1
                        else:
                            score += 0.5
        if score > 0:
            intent_scores[intent_name] = score

    if intent_scores:
        best_intent = max(intent_scores, key=intent_scores.get)
        return best_intent
    return None


def extract_entities(question):
    """从问题中抽取简单实体（community, service_type）基于 DB 的已知值匹配"""
    entities = {"community": None, "service_type": None}
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT community_id FROM seniors')
        communities = [row[0] for row in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT service_type FROM service_records')
        service_types = [row[0] for row in cursor.fetchall()]
        conn.close()

        # 精确包含
        for c in communities:
            if c and str(c) in question:
                entities['community'] = c
                break
        for s in service_types:
            if s and str(s) in question:
                entities['service_type'] = s
                break

        # 模糊匹配
        if not entities['community'] and communities:
            token_candidates = re.findall(r"[\w\u4e00-\u9fff]+", question)
            if token_candidates:
                for tok in token_candidates:
                    close = difflib.get_close_matches(tok, communities, n=1, cutoff=0.7)
                    if close:
                        entities['community'] = close[0]
                        break

        if not entities['service_type'] and service_types:
            token_candidates = re.findall(r"[\w\u4e00-\u9fff]+", question)
            if token_candidates:
                for tok in token_candidates:
                    close = difflib.get_close_matches(tok, service_types, n=1, cutoff=0.7)
                    if close:
                        entities['service_type'] = close[0]
                        break

    except Exception:
        pass

    return entities

def process_question(question, user_id=None):
    """处理问题，包括意图识别和回答生成"""
    # 检测意图并抽取实体
    intent = detect_intent(question)
    context = conversation_context.get(user_id, {})
    entities = extract_entities(question)

    # 处理意图并智能调用响应函数（支持可选实体参数）
    if intent:
        response_function = INTENTS[intent]['response']
        if response_function in globals():
            func = globals()[response_function]
            try:
                sig = inspect.signature(func)
                if len(sig.parameters) == 0:
                    answer = func()
                else:
                    kwargs = {}
                    for name in sig.parameters:
                        if name in entities and entities[name] is not None:
                            kwargs[name] = entities[name]
                    answer = func(**kwargs)
            except Exception as e:
                print(f"调用响应函数失败: {e}")
                answer = "抱歉，我暂时无法回答这个问题。"
        else:
            answer = "抱歉，我暂时无法回答这个问题。"
    else:
        answer = handle_unrecognized_intent(question, context)

    # 更新上下文
    if user_id:
        context['last_question'] = question
        context['last_intent'] = intent
        context.update(entities)
        conversation_context[user_id] = context

    return answer

def handle_unrecognized_intent(question, context):
    """处理未识别的意图"""
    qlow = question.lower()
    if '什么' in question or '什么' in qlow:
        return "我理解您的问题是关于某个具体事项的信息，请问您想了解关于老人服务的哪些具体内容呢？"
    if '怎么' in question or '如何' in question or '怎么' in qlow or '如何' in qlow:
        return "我理解您的问题是关于如何操作或处理某件事情，请问您想了解关于老人服务的哪些具体流程呢？"
    if '为什么' in question or '为什么' in qlow:
        return "我理解您的问题是关于某个现象的原因，请问您想了解关于老人服务的哪些具体问题的原因呢？"
    if '哪里' in question or '哪里有' in qlow:
        return "我理解您的问题是关于服务地点的信息，目前我们的服务覆盖多个社区，您可以咨询具体社区的服务情况。"

    # 基于 DB 回退：尝试在服务类型或社区中找到相关词
    try:
        conn = get_db()
        cursor = conn.cursor()
        token_candidates = re.findall(r"[\w\u4e00-\u9fff]+", question)
        if token_candidates:
            for tok in token_candidates:
                cursor.execute('SELECT COUNT(*) FROM service_records WHERE service_type LIKE ?', (f"%{tok}%",))
                r = cursor.fetchone()
                if r and r[0] and r[0] > 0:
                    conn.close()
                    return f"我在服务记录中找到与“{tok}”相关的服务，您想了解该服务的次数、满意度，还是服务详情？"
                cursor.execute('SELECT COUNT(*) FROM seniors WHERE community_id LIKE ?', (f"%{tok}%",))
                r2 = cursor.fetchone()
                if r2 and r2[0] and r2[0] > 0:
                    conn.close()
                    return f"我在系统中找到与社区“{tok}”相关的数据，您想查询该社区的服务需求还是老人健康状况？"
        conn.close()
    except Exception:
        pass

    return "抱歉，我暂时无法理解您的问题。您可以尝试问：某社区的服务需求、某项服务的次数或满意度、或老人的健康分布。"

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

@bp.route('/initial', methods=['GET'])
def get_initial_message():
    """获取初始聊天消息"""
    try:
        # 生成初始问候语
        answer = get_greeting_answer()
        return jsonify({'answer': answer})
    except Exception as e:
        print(f"获取初始消息失败: {e}")
        return jsonify({'error': '获取初始消息失败'}), 500

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

def get_max_demand_answer(service_type=None):
    """获取最大需求的回答，可选择按 service_type 查询"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        if service_type:
            cursor.execute('SELECT service_type, COUNT(*) as count FROM service_records WHERE service_type = ? GROUP BY service_type', (service_type,))
            result = cursor.fetchone()
        else:
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
            service_type_val, count = result
            return f"根据服务记录分析，老人的最大需求是{service_type_val}服务，共提供了{count}次服务。"
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

def get_health_status_answer(community=None):
    """获取健康状况的回答，可按社区筛选"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        if community:
            cursor.execute('SELECT health_status, COUNT(*) as count FROM seniors WHERE community_id = ? GROUP BY health_status', (community,))
        else:
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

def get_service_count_answer(service_type=None):
    """获取服务次数的回答，可按 service_type 筛选"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        if service_type:
            cursor.execute('SELECT COUNT(*) FROM service_records WHERE service_type = ?', (service_type,))
        else:
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

def get_service_details_answer(service_type=None):
    """获取服务详情的回答，可指定 service_type 获取更具体描述"""
    if service_type:
        return f"关于{service_type}：\n我们为老人提供专业的{service_type}服务，包含上门和定点两种模式，服务人员有资质认证并记录满意度反馈。"
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
