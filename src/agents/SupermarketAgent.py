class SupermarketAgent:
    def __init__(self, agent_id, initial_inventory=1000):
        self.agent_id = agent_id
        self.inventory = initial_inventory
        self.sales = 0
        self.spoilage = 0
        self.stockouts = 0
        
    def process_sales(self, demand):
        """处理居民或团购订单"""
        actual_sales = min(demand, self.inventory)
        self.inventory -= actual_sales
        self.sales += actual_sales
        if demand > actual_sales:
            self.stockouts += (demand - actual_sales)
        return actual_sales
    
    def daily_update(self, season):
        """每日补货与损耗"""
        self.inventory += 100
        spoilage_rate = 0.08 if season == "Summer" else 0.03
        daily_spoilage = self.inventory * spoilage_rate
        self.inventory -= daily_spoilage
        self.spoilage += daily_spoilage
        return daily_spoilage
