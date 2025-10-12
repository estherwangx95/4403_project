import random
import math
import config

class Consumer:
    def __init__(self, id, trust, price_sensitivity, network):
        self.id = id
        self.trust = trust
        self.price_sensitivity = price_sensitivity
        self.network = network  # list of neighbor IDs
        self.purchased = False

    def receive_influence(self, influence, leader_id):
        """根据团长影响力与自身特征决定是否购买"""
        # 使用 sigmoid 函数计算购买概率（更平滑）
        p = 1 / (1 + math.exp(-5 * (self.trust * influence - 0.5 * self.price_sensitivity)))
        p = min(1, max(0, p))  # 确保在 [0, 1]
        
        self.purchased = random.random() < p  # 更新购买状态
        
        # 调试输出
        print(f"🧍‍♀️ Consumer {self.id} | Leader {leader_id} | "
            f"Trust={self.trust:.2f} | Sens={self.price_sensitivity:.2f} | "
            f"Infl={influence:.2f} | Prob={p:.2f} | Buy={self.purchased}")

    def get_neighbors(self):
        """返回部分邻居ID，用于口碑传播"""
        # 根据社会传播经典模型（例如 Rogers, Diffusion of Innovations, 2003）：每个个体只与自己社交圈中约 2–10% 的成员在一次事件中发生信息互动。
        return [n for n in self.network if random.random() < config.DEFAULT_TRUST_DIFFUSION]  # 5% 几率选取邻居


class Leader:
    def __init__(self, id, reputation, connections):
        self.id = id
        self.reputation = reputation
        self.connections = connections

    def promote(self):
        """团长影响力"""
        # 声誉与传播强度的线性映射关系 声誉高 → 影响力强 → 更容易被他人采纳 → 声誉进一步上升。这符合现实中的“马太效应”。
        influence = 0.5 + config.INFLUENCE_STRENGTH * self.reputation
        print(f"👑 Leader {self.id} promotes with influence={influence:.2f}")
        return influence


class Platform:
    def __init__(self, base_price=config.BASE_PRICE, subsidy=config.INITIAL_SUBSIDY):
        self.base_price = base_price
        self.subsidy = subsidy

    def update_policy(self, sales, decay=config.SUBSIDY_DECAY_RATE):
        """根据销量动态调整补贴"""
        self.subsidy *= decay
        if sales < 0.3 * config.N_CONSUMERS:
            self.subsidy += 0.2
        print(f"🏦 Platform updated: sales={sales}, subsidy={self.subsidy:.2f}")
