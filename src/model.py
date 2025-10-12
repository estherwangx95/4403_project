# src/model.py
from agents import Consumer, Leader, Platform
from scheduler import SocialScheduler
import random
import config

class GroupBuyingModel:
    def __init__(self, 
                 n_consumers=config.N_CONSUMERS, 
                 n_leaders=config.N_LEADERS, 
                 base_price=config.BASE_PRICE, 
                 subsidy=config.INITIAL_SUBSIDY):
        """
        n_consumers: 消费者数量
        n_leaders: 团长数量
        base_price: 平台基础定价
        subsidy: 初始补贴
        """
        self.consumers = [
            Consumer(i, random.uniform(0.6, 1.0), random.uniform(0.3, 1.0), list(range(n_consumers)))
            for i in range(n_consumers)
        ]
        connections_per_leader = int(n_consumers * 0.3)  # 30% 的消费者
        self.leaders = [
            Leader(i, random.uniform(0.5, 1.0), random.sample(range(n_consumers), connections_per_leader))
            for i in range(n_leaders)
        ]
        self.platform = Platform(base_price=base_price, subsidy=subsidy)
        self.scheduler = SocialScheduler(self.consumers, self.leaders, self.platform)
        self.sales_record = []          # 每轮销售数量
        self.avg_trust_record = []    # 每轮平均信任
        self.subsidy_record = []      # 平台补贴变化

    def step(self):
        total_sales = self.scheduler.step()
        self.sales_record.append(total_sales)
        # 平均信任
        avg_trust = sum([c.trust for c in self.consumers]) / len(self.consumers)
        self.avg_trust_record.append(avg_trust)

        # 当前补贴
        self.subsidy_record.append(self.platform.subsidy)

    def run_model(self, steps=30, verbose=False):
        for step in range(steps):
            self.step()
            if verbose:
                print(f"Step {step+1}: Sales={self.sales_record[-1]}, AvgTrust={self.avg_trust_record[-1]:.2f}")
        return {
            "sales": self.sales_record,
            "trust": self.avg_trust_record,
            "subsidy": self.subsidy_record
        }