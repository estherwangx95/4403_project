import numpy as np

class GroupLeaderAgent:
    """
    社区团长智能体（简化版）
    - 负责组织团购、议价、协调居民与超市
    - 核心行为：招募成员、议价、下单、分配商品
    """

    def __init__(self, unique_id, model, bargaining_power=None):
        self.unique_id = unique_id
        self.model = model
        self.bargaining_power = bargaining_power or np.random.uniform(0.3, 0.8)
        self.service_fee_rate = 0.1

        # 基本状态
        self.group_members = []
        self.location = np.random.uniform(0, 10, size=2)

        # 数据追踪
        self.total_commission = 0
        self.total_sales_volume = 0
        self.successful_negotiations = 0

    # --- 成员招募 ---
    def recruit_members(self, residents):
        """根据距离与满意度招募成员"""
        for r in residents:
            if r not in self.group_members:
                dist = np.linalg.norm(np.array(r.location) - self.location)
                if dist < 5 and r.satisfaction_level < 0.7:
                    self.group_members.append(r)

    # --- 与超市议价 ---
    def negotiate_price(self, supermarket):
        """基于议价能力和成员数量调整价格"""
        base = supermarket.base_price
        discount = self.bargaining_power * (len(self.group_members) / 50)
        price = max(base * (1 - discount), base * 0.5)
        self.successful_negotiations += 1
        return price

    # --- 组织团购 ---
    def organize_group_purchase(self, supermarket):
        """汇总需求、议价并下单"""
        if not self.group_members:
            return 0

        # 汇总成员需求
        total_demand = sum(r.calculate_demand() for r in self.group_members)
        price = self.negotiate_price(supermarket)

        # 下单与销售
        sales = supermarket.process_groupbuy_order(total_demand, price)
        self.total_sales_volume += sales
        self.total_commission += sales * price * self.service_fee_rate

        self._distribute_goods(sales, price)
        return sales

    # --- 商品分配 ---
    def _distribute_goods(self, total, price):
        """平均分配团购商品"""
        if not self.group_members:
            return
        avg = total / len(self.group_members)
        for r in self.group_members:
            r.inventory_level += avg
            r.last_purchase_price = price
            r.satisfaction_level = min(1.0, r.satisfaction_level + 0.1)

    # --- 每日流程 ---
    def step(self):
        """每周一次团购，其他时间招募成员"""
        if self.model.current_day % 7 == 0:
            self.organize_group_purchase(self.model.supermarket)
        else:
            self.recruit_members(self.model.residents)
