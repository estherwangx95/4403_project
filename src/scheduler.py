# src/scheduler.py
import random

class SocialScheduler:
    def __init__(self, consumers, leaders, platform):
        self.consumers = consumers
        self.leaders = leaders
        self.platform = platform
        self.time = 0

    def step(self):
        print(f"\n================= 🕒 Step {self.time} =================")

        # 1️⃣ 团长影响消费者
        for leader in self.leaders:
            influence = leader.promote()
            for cid in leader.connections:
                consumer = self.consumers[cid]
                consumer.receive_influence(influence, leader.id)

        # 2️⃣ 消费者之间的口碑传播
        for consumer in self.consumers:
            if consumer.purchased:
                neighbors = consumer.get_neighbors()
                for fid in neighbors:
                    friend = self.consumers[fid]
                    # 提升信任幅度更大 高信任的人传播得更有效
                    delta = self.trust * 0.1 * (1 - friend.trust)
                    friend.trust = min(1.0, friend.trust + delta)

        # 3️⃣ 统计销量
        total_sales = sum([1 for c in self.consumers if c.purchased])
        print(f"📊 Total sales this step: {total_sales}")

        # 4️⃣ 平台更新策略
        self.platform.update_policy(total_sales)

        # 5️⃣ 清空购买状态
        for consumer in self.consumers:
            consumer.purchased = False

        self.time += 1
        return total_sales