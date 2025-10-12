# src/model.py
from agents import Consumer, Leader, Platform
from scheduler import SocialScheduler
import random

class GroupBuyingModel:
    def __init__(self, n_consumers=50, n_leaders=3):
        self.consumers = [
            Consumer(i, random.uniform(0.6, 1.0), random.uniform(0.3, 1.0), list(range(n_consumers)))
            for i in range(n_consumers)
        ]
        connections_per_leader = int(n_consumers * 0.3)  # 30% 的消费者
        self.leaders = [
            Leader(i, random.uniform(0.5, 1.0), random.sample(range(n_consumers), connections_per_leader))
            for i in range(n_leaders)
        ]
        self.platform = Platform(base_price=5, subsidy=3)
        self.scheduler = SocialScheduler(self.consumers, self.leaders, self.platform)
        self.sales_record = []

    def step(self):
        total_sales = self.scheduler.step()
        self.sales_record.append(total_sales)