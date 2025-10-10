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

        # 新补充初始化团长的位置（和居民位置逻辑一致，随机生成0-10的坐标）
        self.location = (np.random.uniform(0, 10), np.random.uniform(0, 10))
        
        # ==========  新增：统计当日居民主动发起的团购量  ==========
        self.daily_resident_groupbuy_quantity = 0  # 临时存储当日居民团购量


    def add_groupbuy_quantity(self, quantity):
        """
        新增：接收居民的团购购买量，累计当日总量
        由ResidentAgent的make_purchase_decision调用，统计居民主动选择的团购需求
        """
        self.daily_resident_groupbuy_quantity += quantity


    def recruit_members(self, residents):
        """
        招募居民加入团购组
        基于距离和居民特征的简单逻辑
        """
        for resident in residents:
            # 简单的距离和满意度筛选
            resident_coord = np.array(resident.location)  # 居民坐标转数组
            leader_coord = np.array(self.location)        # 团长坐标转数组
            distance_between = np.linalg.norm(resident_coord - leader_coord)
            is_close_enough = distance_between < 5
            is_dissatisfied = resident.satisfaction_level < 0.7
            is_not_in_group = resident not in self.group_members
            if is_close_enough and is_dissatisfied and is_not_in_group:
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
        组织团购：收集需求（含居民主动团购量）、议价、下单
        ==========  修改：整合“团长主动收集需求”和“居民主动团购量”  ==========
        """
        if not self.group_members:
            # 重置当日团购量（避免空组时残留数据）
            self.daily_resident_groupbuy_quantity = 0
            return 0
        
        # 1. 收集成员主动发起的团购量（从add_groupbuy_quantity累计的数值）
        resident_initiated_demand = self.daily_resident_groupbuy_quantity
        
        # 2. 收集团长主动统计的成员需求（原有逻辑保留）
        leader_initiated_demand = 0
        for resident in self.group_members:
            leader_initiated_demand += resident.calculate_demand()
        
        # 3. 总需求 = 居民主动团购量 + 团长主动统计量
        total_demand = resident_initiated_demand + leader_initiated_demand
        
        # 议价
        final_price = self.negotiate_with_supermarket(supermarket)
        
        # 向超市下单（用总需求计算实际销量）
        actual_sales = supermarket.process_groupbuy_order(total_demand, final_price)
        
        # 计算佣金
        commission = actual_sales * final_price * self.service_fee_rate
        self.total_commission += commission
        self.total_volume_organized += actual_sales
        
        # 分配商品给成员 (简化处理)
        self._distribute_to_members(actual_sales, final_price)
        
        # ==========  新增：重置当日团购量，避免跨周累计  ==========
        self.daily_resident_groupbuy_quantity = 0
        
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
        if self.model.current_day % 7 == 0:  # 每周组织一次团购
            supermarket = self.model.supermarket
            self.organize_group_purchase(supermarket)
            
            # 定期招募新成员
            self.recruit_members(self.model.residents)
        # ==========  新增：非团购日也持续招募成员（扩大用户基数）  ==========
        else:
            self.recruit_members(self.model.residents)
