import numpy as np

class ResidentAgent:
    """
    Resident agent
    --------------
    Represents a household-level demand unit.
    Each resident has unique price sensitivity and group-buying preference.
    """

    def __init__(self, agent_id, household_size, location):
        self.agent_id = agent_id
        self.household_size = household_size
        self.location = location
        self.price_sensitivity = np.random.uniform(0.1, 0.9)   # how strongly demand reacts to price
        self.group_buy_preference = np.random.uniform(0, 1)    # preference for group-buy channel

    def generate_daily_demand(self, day, season):
        """Generate daily demand affected by season and weekend."""
        base = self.household_size * 0.5
        seasonal = 1.2 if season == "Summer" else 0.8 if season == "Winter" else 1.0
        weekend = 1.3 if day % 7 in [5, 6] else 1.0
        return base * seasonal * weekend

    def choose_purchase_channel(self, supermarket_price, groupbuy_price):
        """Choose between supermarket and group-buy based on price gap and preference."""
        diff = supermarket_price - groupbuy_price
        threshold = 0.1 + self.group_buy_preference * 0.3
        return "groupbuy" if diff > threshold else "supermarket"
