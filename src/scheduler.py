import config
import numpy as np

class SocialScheduler:
    def __init__(self, consumers, leaders, platform):
        self.consumers = consumers
        self.leaders = leaders
        self.platform = platform
        self.time = 0

    def step(self):
        print(f"\n================= Step {self.time} =================")

        total_sales = 0
        # leaders impact on consumers
        for leader in self.leaders:
            influence = leader.reputation * config.INFLUENCE_STRENGTH
            print(f"👑 Leader {leader.id} promotes with influence={influence:.2f}")
            for cid in leader.connections:
                consumer = self.consumers[cid]
                consumer.receive_influence(influence, leader.id)
                if consumer.purchased:
                    total_sales += 1

        # The spread of trust among consumers
        for consumer in self.consumers:
            if consumer.purchased:
                for fid in consumer.get_neighbors():
                    friend = self.consumers[fid]
                    delta = config.TRUST_GROWTH_RATE * (1 - friend.trust)
                    friend.trust = min(1.0, friend.trust + delta)


        # Count sales volume
        avg_trust = np.mean([c.trust for c in self.consumers])
        subsidy = self.platform.subsidy

        print(f" Total sales this step: {total_sales}")
        print(f" Average trust: {avg_trust:.3f}")
        print(f" Current subsidy: {subsidy:.3f}")

        # Platform update strategy
        self.platform.update_policy(total_sales)

        # Empty purchase status
        for consumer in self.consumers:
            consumer.purchased = False

        self.time += 1
        return total_sales, avg_trust, subsidy
