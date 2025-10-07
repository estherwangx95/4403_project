# src/agents/resident_agent.py
import numpy as np

class ResidentAgent:
    """
    居民智能体类
    模拟社区居民的购买决策行为，基于家庭特征和经济理性
    """
    
    def __init__(self, unique_id, model, household_size, income_level, location):
        """
        初始化居民智能体
        
        参数依据：
        - household_size: 基于ABS Census 2021家庭规模分布
        - income_level: 基于澳大利亚收入分层数据
        - price_sensitivity: 基于Chen et al. (2020)消费者行为研究
        """
        self.unique_id = unique_id
        self.model = model
        self.household_size = household_size
        
        # 收入水平 (1:低收入, 2:中等收入, 3:高收入)
        self.income_level = income_level  
        
        # 位置坐标 (用于空间交互)
        self.location = location
        
        # 行为参数
        self.price_sensitivity = self._calculate_price_sensitivity()
        self.loyalty_factor = np.random.uniform(0.1, 0.9)  # 品牌/渠道忠诚度
        
        # 状态变量
        self.inventory_level = 0  # 当前库存水平
        self.satisfaction_level = 1.0  # 满意度
        self.last_purchase_price = 0
        self.days_since_last_purchase = 0
        
        # 决策历史
        self.purchase_history = []
    
    def _calculate_price_sensitivity(self):
        """
        基于收入水平计算价格敏感度
        理论依据：微观经济学需求弹性理论 (Chen et al., 2020)
        """
        if self.income_level == 1:  # 低收入群体
            return np.random.uniform(0.7, 0.9)  # 高敏感度
        elif self.income_level == 2:  # 中等收入
            return np.random.uniform(0.4, 0.6)  # 中等敏感度
        else:  # 高收入
            return np.random.uniform(0.1, 0.3)  # 低敏感度
    
    def calculate_demand(self):
        """
        计算每日需求
        基于家庭规模和随机波动
        数据依据：AC Nielsen零售数据
        """
        base_demand = 0.1 * self.household_size  # 基础需求率
        noise = np.random.normal(0, 0.05)  # 随机波动
        return max(0, base_demand + noise)
    
    def make_purchase_decision(self, supermarket_price, groupbuy_price=None):
        """
        购买决策逻辑
        基于价格比较、满意度、忠诚度的综合决策
        """
        # 计算库存压力 (库存越低，购买意愿越强)
        inventory_pressure = max(0, 1 - self.inventory_level)
        
        # 基础购买概率
        base_probability = 0.3 * inventory_pressure
        
        if groupbuy_price is not None:
            # 有团购选项时的决策逻辑
            price_difference = supermarket_price - groupbuy_price
            price_advantage = price_difference / supermarket_price if supermarket_price > 0 else 0
            
            # 团购购买概率 = 基础概率 + 价格优势效应 + 满意度影响
            groupbuy_prob = (base_probability + 
                           price_advantage * self.price_sensitivity + 
                           (self.satisfaction_level - 0.5) * 0.2)
            
            groupbuy_prob = np.clip(groupbuy_prob, 0, 0.8)  # 概率上限
            
            # 决策
            if np.random.random() < groupbuy_prob:
                self._execute_purchase(groupbuy_price, "groupbuy")
                return "groupbuy"
        
        # 超市购买决策
        supermarket_prob = base_probability - (0.1 * self.price_sensitivity)
        supermarket_prob = np.clip(supermarket_prob, 0, 0.6)
        
        if np.random.random() < supermarket_prob:
            self._execute_purchase(supermarket_price, "supermarket")
            return "supermarket"
        
        return "no_purchase"
    
    def _execute_purchase(self, price, channel):
        """
        执行购买行为，更新状态
        """
        purchase_quantity = self.calculate_demand()
        
        # 更新状态
        self.inventory_level += purchase_quantity
        self.last_purchase_price = price
        self.days_since_last_purchase = 0
        
        # 记录历史
        self.purchase_history.append({
            'day': self.model.schedule.time,
            'channel': channel,
            'price': price,
            'quantity': purchase_quantity
        })
        
        # 更新满意度 (价格越低，满意度越高)
        price_satisfaction = 1 - (price * self.price_sensitivity / 10)
        self.satisfaction_level = 0.7 * self.satisfaction_level + 0.3 * price_satisfaction
        
        return purchase_quantity
    
    def step(self):
        """
        每个时间步执行的行为
        """
        # 每日库存消耗
        self.inventory_level = max(0, self.inventory_level - self.calculate_demand() * 0.5)
        self.days_since_last_purchase += 1
        
        # 满意度自然衰减
        self.satisfaction_level *= 0.98
