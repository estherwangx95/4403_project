from datetime import datetime, timedelta
import numpy as np

class EnhancedMarketEnvironment:
    """
    Market environment
    ------------------
    Manages season effects, external shocks, and basic system stats.
    """

    def __init__(self, start_date=None):
        # Time control
        self.current_date = start_date or datetime(2023, 1, 1)
        self.day_of_year = self.current_date.timetuple().tm_yday

        # Seasonal multipliers
        self.seasonal_factors = {
            "Spring": 1.0,
            "Summer": 1.3,
            "Autumn": 0.9,
            "Winter": 0.7
        }

        # External shocks (temporary demand/supply changes)
        self.shocks = {}  # {type: {'magnitude': x, 'end_day': y}}

        # Logs
        self.demand_log = []
        self.spoilage_log = []
        self.price_log = []

    # ---------------------------------------------------------------
    def get_season(self):
        """Return current season name."""
        d = self.day_of_year
        if 80 <= d <= 172:
            return "Spring"
        elif 173 <= d <= 265:
            return "Summer"
        elif 266 <= d <= 355:
            return "Autumn"
        return "Winter"

    # ---------------------------------------------------------------
    def get_season_factor(self):
        """Return seasonal multiplier."""
        return self.seasonal_factors[self.get_season()]

    # ---------------------------------------------------------------
    def apply_shock(self, shock_type, magnitude=0.5, duration=7):
        """Add temporary external shock."""
        end_day = self.day_of_year + duration
        self.shocks[shock_type] = {"magnitude": magnitude, "end_day": end_day}

    def update_shocks(self):
        """Remove expired shocks."""
        active = {}
        for k, v in self.shocks.items():
            if self.day_of_year < v["end_day"]:
                active[k] = v
        self.shocks = active

    # ---------------------------------------------------------------
    def demand_multiplier(self):
        """Combine effects of season and external shocks."""
        factor = self.get_season_factor()
        if "demand_spike" in self.shocks:
            factor *= (1 + self.shocks["demand_spike"]["magnitude"])
        if "supply_chain_disruption" in self.shocks:
            factor *= (1 - self.shocks["supply_chain_disruption"]["magnitude"] * 0.5)
        return max(0.1, factor)

    # ---------------------------------------------------------------
    def record_day(self, demand, spoilage, price):
        """Record key daily metrics."""
        self.demand_log.append(demand)
        self.spoilage_log.append(spoilage)
        self.price_log.append(price)

    # ---------------------------------------------------------------
    def next_day(self):
        """Advance simulation by one day."""
        self.current_date += timedelta(days=1)
        self.day_of_year = self.current_date.timetuple().tm_yday
        self.update_shocks()
