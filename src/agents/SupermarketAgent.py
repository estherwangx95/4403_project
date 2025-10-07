# src/agents/supermarket_agent.py
import numpy as np

class SupermarketAgent:
    """
    超市智能体类
    模拟超市的库存管理、定价和运营决策
    """
    
    def __init__(self, unique_id, model, capacity=1000):
        self.unique_id = unique_id
        self.model = model
        
        # 运营参数 (依据：FAO食物浪费报告，行业基准)
        self.capacity = capacity  # 库存容量
        self.base_spoilage_rate = 0.03  # 基础损耗率 3%
        self.seasonal_multiplier = 1.0   # 季节乘数
        
        # 状态变量
        self.inventory_level = capacity * 0.8  # 初始库存
        self.daily_demand = 0
        self.total_spoilage = 0
        self.revenue = 0
        
        # 策略参数
        self.base_price = 10.0  # 基础价格
        self.reorder_point = capacity * 0.3  # 再订货点
        self.reorder_quantity = capacity * 0.5  # 订货量
    
    def calculate_spoilage_rate(self):
        """
        计算当日损耗率
        依据：FAO食物浪费报告，夏季损耗率升高
        """
        seasonal_effect = self.model.get_seasonal_factor()  # 从环境获取季节因子
        return self.base_spoilage_rate * seasonal_effect
    
    def process_demand(self, demand_quantity):
        """
        处理居民需求
        """
        actual_sales = min(demand_quantity, self.inventory_level)
        self.inventory_level -= actual_sales
        self.daily_demand += actual_sales
        self.revenue += actual_sales * self.base_price
        
        return actual_sales
    
    def process_groupbuy_order(self, total_quantity, negotiated_price):
        """
        处理团长的大宗订单
        """
        actual_sales = min(total_quantity, self.inventory_level)
        self.inventory_level -= actual_sales
        self.revenue += actual_sales * negotiated_price
        
        return actual_sales
    
    def update_inventory(self):
        """
        更新库存，计算损耗
        """
        # 计算损耗
        spoilage_rate = self.calculate_spoilage_rate()
        spoilage_amount = self.inventory_level * spoilage_rate
        self.inventory_level -= spoilage_amount
        self.total_spoilage += spoilage_amount
        
        # 自动补货逻辑
        if self.inventory_level < self.reorder_point:
            self.inventory_level += self.reorder_quantity
    
    def step(self):
        """
        每日运营流程
        """
        self.update_inventory()
        self.daily_demand = 0  # 重置日需求记录