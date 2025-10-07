# src/agents/group_leader_agent.py
import numpy as np

class GroupLeaderAgent:
    """
    团长智能体类
    模拟社区团购团长的协调、议价和组织行为
    """
    
    def __init__(self, unique_id, model, bargaining_power=None):
        self.unique_id = unique_id
        self.model = model
        
        # 能力参数 (依据：平台经济研究报告)
        self.bargaining_power = (bargaining_power if bargaining_power is not None 
                               else np.random.uniform(0.3, 0.8))
        self.service_fee_rate = 0.10  # 服务费率 10%
        
        # 运营状态
        self.group_members = []  # 团组成员
        self.current_order_volume = 0
        self.negotiated_price = 0
        self.total_commission = 0
        
        # 性能指标
        self.successful_negotiations = 0
        self.total_volume_organized = 0
    
    def recruit_members(self, residents):
        """
        招募居民加入团购组
        基于距离和居民特征的简单逻辑
        """
        for resident in residents:
            # 简单的距离和满意度筛选
            distance = np.linalg.norm(
                np.array(resident.location) - np.array(self.model.leader_location)
            )
            if (distance < 5 and 
                resident.satisfaction_level < 0.7 and 
                resident not in self.group_members):
                self.group_members.append(resident)
    
    def negotiate_with_supermarket(self, supermarket):
        """
        与超市议价
        基于议价能力和订单规模
        """
        base_price = supermarket.base_price
        volume_factor = len(self.group_members) / 50  # 规模效应
        
        # 议价公式：基础价格 × (1 - 议价能力 × 规模因子)
        self.negotiated_price = base_price * (
            1 - self.bargaining_power * volume_factor
        )
        
        # 确保价格合理
        self.negotiated_price = max(self.negotiated_price, base_price * 0.5)
        
        self.successful_negotiations += 1
        return self.negotiated_price
    
    def organize_group_purchase(self, supermarket):
        """
        组织团购：收集需求、议价、下单
        """
        if not self.group_members:
            return 0
        
        # 收集成员需求
        total_demand = 0
        for resident in self.group_members:
            demand = resident.calculate_demand()
            total_demand += demand
        
        # 议价
        final_price = self.negotiate_with_supermarket(supermarket)
        
        # 向超市下单
        actual_sales = supermarket.process_groupbuy_order(total_demand, final_price)
        
        # 计算佣金
        commission = actual_sales * final_price * self.service_fee_rate
        self.total_commission += commission
        self.total_volume_organized += actual_sales
        
        # 分配商品给成员 (简化处理)
        self._distribute_to_members(actual_sales, final_price)
        
        return actual_sales
    
    def _distribute_to_members(self, total_quantity, price):
        """
        将团购商品分配给成员 (简化版本)
        """
        avg_quantity = total_quantity / len(self.group_members) if self.group_members else 0
        
        for resident in self.group_members:
            # 更新居民状态
            resident.inventory_level += avg_quantity
            resident.last_purchase_price = price
            resident.satisfaction_level = min(1.0, resident.satisfaction_level + 0.1)
    
    def step(self):
        """
        团长每日工作流程
        """
        if self.model.schedule.time % 7 == 0:  # 每周组织一次团购
            supermarket = self.model.supermarket
            self.organize_group_purchase(supermarket)
            
            # 定期招募新成员
            self.recruit_members(self.model.residents)