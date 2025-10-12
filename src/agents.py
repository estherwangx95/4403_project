# ============================================================
# agents.py — Agent Classes for Community Group Buying
# ============================================================

import random
import config

# ---- 🧍 Consumer ----
class Consumer:
    def __init__(self, cid, trust, price_sensitivity, neighbors):
        self.id = cid
        self.trust = trust
        self.price_sensitivity = price_sensitivity
        self.neighbors = neighbors
        self.purchased = False

    def get_neighbors(self):
        """返回部分邻居用于信任传播"""
        n_neighbors = max(1, int(len(self.neighbors) * 0.1))
        return random.sample(self.neighbors, n_neighbors)


# ---- 👑 Leader ----
class Leader:
    def __init__(self, lid, reputation, connections):
        self.id = lid
        self.reputation = reputation
        self.connections = connections


# ---- 🏦 Platform ----
class Platform:
    def __init__(self, base_price=config.BASE_PRICE, subsidy=config.INITIAL_SUBSIDY):
        self.base_price = base_price
        self.subsidy = subsidy

    def update_subsidy(self, total_sales, decay=0.95):
        """根据销量调整补贴"""
        self.subsidy *= decay
        if total_sales < 0.3 * config.N_CONSUMERS:
            self.subsidy += 0.2