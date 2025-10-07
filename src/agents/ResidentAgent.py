import numpy as np

class ResidentAgent:
    def __init__(self, agent_id, household_size, location):
        self.agent_id = agent_id
        self.household_size = household_size
        self.location = location
        self.price_sensitivity = np.random.uniform(0.1, 0.9)
        self.group_buy_preference = np.random.uniform(0, 1)
        
    def generate_daily_demand(self, day, season):
        """生成每日需求，受季节与周末影响"""
        base_demand = self.household_size * 0.5
        seasonal_factor = 1.2 if season == "Summer" else 0.8 if season == "Winter" else 1.0
        weekend_factor = 1.3 if day % 7 in [5, 6] else 1.0
        return base_demand * seasonal_factor * weekend_factor
    
    def choose_purchase_channel(self, supermarket_price, groupbuy_price):
        """基于价格差与偏好选择购买渠道"""
        price_difference = supermarket_price - groupbuy_price
        threshold = 0.1 + self.group_buy_preference * 0.3
        return "groupbuy" if price_difference > threshold else "supermarket"
