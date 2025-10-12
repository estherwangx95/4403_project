# ============================================================
# scheduler.py — SocialScheduler with Config Integration
# ============================================================

import random
import config

class SocialScheduler:
    """
    调度器：协调团长推广、消费者购买、信任传播与平台反馈。
    """
    def __init__(self, consumers, leaders, platform):
        self.consumers = consumers
        self.leaders = leaders
        self.platform = platform

    def step(self):
        """执行一次完整调度周期"""
        total_sales = 0

        # === 1️⃣ 团长影响阶段 ===
        for leader in self.leaders:
            influence = leader.reputation * config.INFLUENCE_STRENGTH
            for cid in leader.connections:
                consumer = self.consumers[cid]
                p = consumer.trust * influence / (1 + consumer.price_sensitivity)
                consumer.purchased = random.random() < p
                if consumer.purchased:
                    total_sales += 1

        # === 2️⃣ 信任传播阶段 ===
        for consumer in self.consumers:
            if consumer.purchased:
                neighbors = consumer.get_neighbors()
                k = max(1, int(len(neighbors) * config.DEFAULT_TRUST_DIFFUSION))
                for fid in random.sample(neighbors, k):
                    friend = self.consumers[fid]
                    delta = config.TRUST_GROWTH_RATE * (1 - friend.trust)
                    friend.trust = min(1.0, friend.trust + delta)

        # === 3️⃣ 平台补贴动态调整 ===
        self.platform.update_subsidy(total_sales, decay=config.SUBSIDY_DECAY_RATE)

        if config.VERBOSE:
            print(f"💡 Step result: Sales={total_sales}, Subsidy={self.platform.subsidy:.2f}")

        return total_sales