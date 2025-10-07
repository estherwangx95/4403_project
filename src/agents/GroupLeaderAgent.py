class GroupBuyLeaderAgent:
    def __init__(self, agent_id, negotiation_power=0.7):
        self.agent_id = agent_id
        self.negotiation_power = negotiation_power
        self.collected_orders = 0
        self.successful_orders = 0
        
    def collect_orders(self, resident_demands):
        total = sum(resident_demands.values())
        self.collected_orders = total
        return total
    
    def negotiate_price(self, base_price, total_quantity):
        """数量折扣 + 团长议价折扣"""
        quantity_discount = min(0.2, total_quantity / 500 * 0.1)
        negotiation_discount = self.negotiation_power * 0.15
        return base_price * (1 - (0.05 + quantity_discount + negotiation_discount))
    
    def distribute_goods(self, received_goods, resident_orders):
        total_ordered = sum(resident_orders.values())
        if received_goods >= total_ordered:
            self.successful_orders = total_ordered
            return resident_orders
        ratio = received_goods / total_ordered
        distributed = {r: d * ratio for r, d in resident_orders.items()}
        self.successful_orders = received_goods
        return distributed
