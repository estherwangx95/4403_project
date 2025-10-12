
from agents import Consumer, Leader, Platform
from scheduler import SocialScheduler
import random
import config

class GroupBuyingModel:
    def __init__(self, n_consumers=config.N_CONSUMERS, n_leaders=config.N_LEADERS):
        self.consumers = [
            Consumer(i, random.uniform(0.4, 0.9), random.uniform(0.2, 1.0), list(range(n_consumers)))
            for i in range(n_consumers)
        ]
        connections_per_leader = int(n_consumers * config.LEADER_CONNECTION_RATIO)  # 30% 的消费者
        self.leaders = [
            Leader(i, random.uniform(0.6, 1.0), random.sample(range(n_consumers), connections_per_leader))
            for i in range(n_leaders)
        ]
        self.platform = Platform(base_price=config.BASE_PRICE, subsidy=config.INITIAL_SUBSIDY)
        self.scheduler = SocialScheduler(self.consumers, self.leaders, self.platform)
        self.sales_record = []
        self.avg_trust_record = []
        self.subsidy_record = []

    def step(self):
        total_sales, avg_trust, subsidy = self.scheduler.step()
        self.sales_record.append(total_sales)
        self.avg_trust_record.append(avg_trust)
        self.subsidy_record.append(subsidy)