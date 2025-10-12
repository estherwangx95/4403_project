# src/scheduler.py
import random
import config
import numpy as np

class SocialScheduler:
    def __init__(self, consumers, leaders, platform):
        self.consumers = consumers
        self.leaders = leaders
        self.platform = platform
        self.time = 0

    def step(self):
        print(f"\n================= 🕒 Step {self.time} =================")

        total_sales = 0
        # 1️⃣ 团长影响消费者
        for leader in self.leaders:
            influence = leader.reputation * config.INFLUENCE_STRENGTH
            print(f"👑 Leader {leader.id} promotes with influence={influence:.2f}")
            for cid in leader.connections:
                consumer = self.consumers[cid]
                consumer.receive_influence(influence, leader.id)
                if consumer.purchased:
                    total_sales += 1

        # 2️⃣ 消费者之间的信任扩散
        for consumer in self.consumers:
            if consumer.purchased:
                for fid in consumer.get_neighbors():
                    friend = self.consumers[fid]
                    delta = config.TRUST_GROWTH_RATE * (1 - friend.trust)
                    friend.trust = min(1.0, friend.trust + delta)


        # 3️⃣ 统计销量
        avg_trust = np.mean([c.trust for c in self.consumers])
        subsidy = self.platform.subsidy

        print(f"📊 Total sales this step: {total_sales}")
        print(f"💬 Average trust: {avg_trust:.3f}")
        print(f"💰 Current subsidy: {subsidy:.3f}")

        # 4️⃣ 平台更新策略
        self.platform.update_policy(total_sales)

        # 5️⃣ 清空购买状态
        for consumer in self.consumers:
            consumer.purchased = False

        self.time += 1
        return total_sales, avg_trust, subsidy