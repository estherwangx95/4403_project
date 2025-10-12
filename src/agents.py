# src/agents.py
import random
import math

class Consumer:
    def __init__(self, id, trust, price_sensitivity, network):
        self.id = id
        self.trust = trust
        self.price_sensitivity = price_sensitivity
        self.network = network  # list of neighbor IDs
        self.purchased = False

    def receive_influence(self, influence, leader_id):
        """根据团长影响力与自身特征决定是否购买"""
        # 更稳定的购买决策概率 sigmoid 更贴近真实社会行为 当代理的信任（trust）乘以影响力（influence）较高时，行为发生（例如购买、采纳意见等）的概率上升；而价格敏感度越高，会抵消一部分正向影响。
        p = 1 / (1 + math.exp(-5 * (self.trust * influence - 0.5 * self.price_sensitivity)))
        p = min(1, max(0, p))  # 确保在 [0, 1]
        decision = random.random() < p
        if decision:
            self.purchased = True
        # 调试输出
        print(f"🧍‍♀️ Consumer {self.id} | Leader {leader_id} | Trust={self.trust:.2f} | Sens={self.price_sensitivity:.2f} | Infl={influence:.2f} | Prob={p:.2f} | Buy={decision}")

    def get_neighbors(self):
        """返回部分邻居ID，用于口碑传播"""
        # 根据社会传播经典模型（例如 Rogers, Diffusion of Innovations, 2003）：每个个体只与自己社交圈中约 2–10% 的成员在一次事件中发生信息互动。
        return [n for n in self.network if random.random() < 0.05]  # 5% 几率选取邻居


class Leader:
    def __init__(self, id, reputation, connections):
        self.id = id
        self.reputation = reputation
        self.connections = connections

    def promote(self):
        """团长影响力"""
        # 声誉与传播强度的线性映射关系 声誉高 → 影响力强 → 更容易被他人采纳 → 声誉进一步上升。这符合现实中的“马太效应”。
        influence = 0.5 + 0.5 * self.reputation
        print(f"👑 Leader {self.id} promotes with influence={influence:.2f}")
        return influence


class Platform:
    def __init__(self, base_price=5, subsidy=2):
        self.base_price = base_price
        self.subsidy = subsidy

    def update_policy(self, sales):
        """根据销量动态调整补贴"""
        if sales > 10:
            self.subsidy *= 0.95
        else:
            self.subsidy *= 1.05
        print(f"🏦 Platform updated: sales={sales}, subsidy={self.subsidy:.2f}")