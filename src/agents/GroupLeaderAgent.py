import numpy as np

class GroupLeaderAgent:
    """
    Group Leader Agent
    ------------------
    Simulates a community group-buying leader who coordinates 
    between residents (demand side) and the supermarket (supply side).

    Main roles:
      • Recruit nearby residents with similar needs
      • Negotiate bulk price with the supermarket
      • Organize group purchase and distribute goods
      • Track commission and group performance
    """

    def __init__(self, unique_id, model, bargaining_power=None):
        """
        Args:
            unique_id (int): Unique agent ID
            model: Reference to the simulation model
            bargaining_power (float, optional): Negotiation strength [0.3–0.8]
        """
        self.unique_id = unique_id
        self.model = model
        self.bargaining_power = bargaining_power or np.random.uniform(0.3, 0.8)
        self.service_fee_rate = 0.10  # 10% commission

        # Basic state
        self.group_members = []
        self.location = np.random.uniform(0, 10, size=2)

        # Stats
        self.total_commission = 0.0
        self.total_sales_volume = 0.0
        self.successful_negotiations = 0

    # ------------------------------------------------------------------
    def recruit_members(self, residents):
        """
        Recruit residents within distance < 5 who have low satisfaction.
        """
        for r in residents:
            if r not in self.group_members:
                dist = np.linalg.norm(np.array(r.location) - self.location)
                if dist < 5 and r.satisfaction_level < 0.7:
                    self.group_members.append(r)

    # ------------------------------------------------------------------
    def negotiate_price(self, supermarket):
        """
        Negotiate price with supermarket.
        Formula:
            price = base_price * (1 - bargaining_power * group_size / 50)
        Min cap = 50% of base price.
        """
        base = supermarket.base_price
        discount = self.bargaining_power * (len(self.group_members) / 50)
        price = max(base * (1 - discount), base * 0.5)

        self.successful_negotiations += 1
        return price

    # ------------------------------------------------------------------
    def organize_group_purchase(self, supermarket):
        """
        Run the full group-buy process:
          1. Collect members' demand
          2. Negotiate price
          3. Submit bulk order
          4. Distribute goods and update stats
        """
        if not self.group_members:
            return 0.0

        # Total demand from all members
        total_demand = sum(r.calculate_demand() for r in self.group_members)
        price = self.negotiate_price(supermarket)

        # Process order and record results
        sales = supermarket.process_groupbuy_order(total_demand, price)
        self.total_sales_volume += sales
        self.total_commission += sales * price * self.service_fee_rate

        self._distribute_goods(sales, price)
        return sales

    # ------------------------------------------------------------------
    def _distribute_goods(self, total_quantity, price):
        """
        Distribute purchased goods equally to members.
        Slight satisfaction gain after each successful order.
        """
        if not self.group_members:
            return

        avg_share = total_quantity / len(self.group_members)
        for r in self.group_members:
            r.inventory_level += avg_share
            r.last_purchase_price = price
            r.satisfaction_level = min(1.0, r.satisfaction_level + 0.1)

    # ------------------------------------------------------------------
    def step(self):
        """
        Weekly group-buy (every 7 days).
        Other days: keep recruiting members.
        """
        if self.model.current_day % 7 == 0:
            self.organize_group_purchase(self.model.supermarket)
        else:
            self.recruit_members(self.model.residents)
