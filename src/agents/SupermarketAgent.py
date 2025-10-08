import numpy as np

class SupermarketAgent:
    """
    Supermarket agent
    -----------------
    Handles inventory, daily spoilage, and order processing.
    """

    def __init__(self, agent_id, initial_inventory=1000):
        self.agent_id = agent_id
        self.inventory = initial_inventory
        self.sales = 0
        self.spoilage = 0
        self.stockouts = 0

    def process_sales(self, demand):
        """Process individual or group orders."""
        actual = min(demand, self.inventory)
        self.inventory -= actual
        self.sales += actual
        if demand > actual:
            self.stockouts += demand - actual
        return actual

    def daily_update(self, season):
        """Restock and apply daily spoilage."""
        self.inventory += 100  # fixed restock
        spoilage_rate = 0.08 if season == "Summer" else 0.03
        spoiled = self.inventory * spoilage_rate
        self.inventory -= spoiled
        self.spoilage += spoiled
        return spoiled
