"""服务服务模块

处理服务使用频次、满意度等业务逻辑
"""

from app.utils.database import db

class ServiceService:
    """服务服务类"""
    
    def get_service_frequency(self):
        """
        获取服务使用频次
        
        返回值：
        - dict: 服务使用频次数据
        """
        query = '''
        SELECT service_type, COUNT(*) as count 
        FROM service_log 
        GROUP BY service_type
        '''
        
        result = db.execute(query)
        
        # 定义服务类型顺序
        service_types = ['助餐', '助医', '保洁', '陪护', '康复']
        counts = {service: 0 for service in service_types}
        
        # 填充数据
        for service, count in result:
            if service in counts:
                counts[service] = int(count)
        
        return {
            'types': service_types,
            'counts': [counts[service] for service in service_types]
        }
    
    def get_service_frequency_by_community(self):
        """
        按社区分析服务使用频次
        
        返回值：
        - dict: 按社区分析的服务使用频次数据
        """
        query = '''
        SELECT community_id, service_type, COUNT(*) as count
        FROM service_log
        GROUP BY community_id, service_type
        ORDER BY community_id
        '''
        
        result = db.execute(query)
        
        # 处理结果
        communities = set()
        service_types = ['助餐', '助医', '保洁', '陪护', '康复']
        
        for community, _, _ in result:
            communities.add(community)
        communities = sorted(communities)
        
        data = {community: {service: 0 for service in service_types} for community in communities}
        
        for community, service, count in result:
            if community in data and service in data[community]:
                data[community][service] = int(count)
        
        # 转换为前端期望的格式
        datasets = []
        for service in service_types:
            dataset = {
                'name': service,
                'data': [data[community][service] for community in communities]
            }
            datasets.append(dataset)
        
        return {
            'communities': communities,
            'datasets': datasets
        }
    
    def get_service_satisfaction(self):
        """
        获取服务满意度
        
        返回值：
        - dict: 服务满意度数据
        """
        query = '''
        SELECT service_type, AVG(satisfaction) as avg_satisfaction
        FROM service_log
        WHERE satisfaction IS NOT NULL
        GROUP BY service_type
        '''
        
        result = db.execute(query)
        
        # 定义服务类型顺序
        service_types = ['助餐', '助医', '保洁', '陪护', '康复']
        satisfaction = {service: 0.0 for service in service_types}
        
        # 填充数据
        for service, avg_sat in result:
            if service in satisfaction:
                satisfaction[service] = float(avg_sat)
        
        return {
            'types': service_types,
            'satisfaction': [satisfaction[service] for service in service_types]
        }
    
    def get_service_trend(self):
        """
        获取服务使用趋势
        
        返回值：
        - dict: 服务使用趋势数据
        """
        query = '''
        SELECT 
            strftime('%Y-%m', service_date) as month,
            service_type,
            COUNT(*) as count
        FROM service_log
        GROUP BY month, service_type
        ORDER BY month
        '''
        
        result = db.execute(query)
        
        # 处理结果
        months = []
        service_types = ['助餐', '助医', '保洁', '陪护', '康复']
        data = {service: [] for service in service_types}
        
        # 收集所有月份
        month_set = set()
        for month, _, _ in result:
            month_set.add(month)
        months = sorted(month_set)
        
        # 重新查询获取完整数据
        result = db.execute(query)
        temp_data = {month: {service: 0 for service in service_types} for month in months}
        
        for month, service, count in result:
            if month in temp_data and service in temp_data[month]:
                temp_data[month][service] = int(count)
        
        # 构建返回数据
        for service in service_types:
            data[service] = [temp_data[month][service] for month in months]
        
        # 转换为前端期望的格式
        datasets = []
        for service in service_types:
            dataset = {
                'name': service,
                'data': data[service]
            }
            datasets.append(dataset)
        
        return {
            'dates': months,
            'datasets': datasets
        }
