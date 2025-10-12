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
        """Decide whether to purchase based on leader influence and own characteristics"""
        # Use sigmoid function to calculate purchase probability (smoother)
        p = 1 / (1 + math.exp(-5 * (self.trust * influence - 0.5 * self.price_sensitivity)))
        p = min(1, max(0, p))  # Ensure probability is in [0, 1]
        
        self.purchased = random.random() < p  # Update purchase status
        
        # Debug output
        print(f"🧍‍♀️ Consumer {self.id} | Leader {leader_id} | "
            f"Trust={self.trust:.2f} | Sens={self.price_sensitivity:.2f} | "
            f"Infl={influence:.2f} | Prob={p:.2f} | Buy={self.purchased}")

    def get_neighbors(self):
        """Return partial neighbor IDs for word-of-mouth propagation"""
        # Based on classic social diffusion models (e.g., Rogers, Diffusion of Innovations, 2003): each individual only interacts with about 2-10% of members in their social circle during one event.
        return [n for n in self.network if random.random() < config.DEFAULT_TRUST_DIFFUSION]  # 5% chance to select neighbors


class Leader:
    def __init__(self, id, reputation, connections):
        self.id = id
        self.reputation = reputation
        self.connections = connections

    def promote(self):
        """Leader influence"""
        # Linear mapping relationship between reputation and propagation strength: high reputation → strong influence → easier adoption by others → further reputation increase. This conforms to the "Matthew Effect" in reality.
        influence = 0.5 + config.INFLUENCE_STRENGTH * self.reputation
        print(f"👑 Leader {self.id} promotes with influence={influence:.2f}")
        return influence


class Platform:
    def __init__(self, base_price=config.BASE_PRICE, subsidy=config.INITIAL_SUBSIDY):
        self.base_price = base_price
        self.subsidy = subsidy

    def update_policy(self, sales, decay=config.SUBSIDY_DECAY_RATE):
        """Dynamically adjust subsidy based on sales"""
        self.subsidy *= decay
        if sales < 0.3 * config.N_CONSUMERS:
            self.subsidy += 0.2
        print(f"🏦 Platform updated: sales={sales}, subsidy={self.subsidy:.2f}")
