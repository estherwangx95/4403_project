import numpy as np
import pandas as pd
import networkx as nx
from scipy.stats import linregress
from collections import defaultdict
from src.agents.resident_agent import ResidentAgent
from src.agents.supermarket_agent import SupermarketAgent
from src.agents.group_leader_agent import GroupLeaderAgent
from src.environment.enhanced_market_environment import EnhancedMarketEnvironment
from src.metrics.complexity_metrics import ComplexityMetrics


class EnhancedMinimalMarketABM:
    """
    Enhanced Minimal Market ABM
    -------------------------------------
    An improved version of the baseline agent-based model that integrates:
    - Social network structure for resident agents
    - Dynamic price feedback mechanism
    - External environmental shocks
    - Real-time complexity and stability tracking
    
    Research goal:
    To investigate how the presence of a group-buying leader
    affects system complexity, stability, and emergent coordination.
    """

    def __init__(self, num_residents=50, has_groupbuy=True, random_seed=42):
        # Fix the random seed for reproducibility
        np.random.seed(random_seed)

        # Basic configuration
        self.num_residents = num_residents
        self.has_groupbuy = has_groupbuy
        self.current_day = 0
        self.is_running = True

        # Core system components
        self.environment = EnhancedMarketEnvironment()
        self.complexity_tracker = ComplexityMetrics()
        self.supermarket = SupermarketAgent(unique_id=0, model=self)
        self.leader = GroupLeaderAgent(unique_id=1, model=self) if has_groupbuy else None

        # Create resident agents with a small-world social network
        self.residents = self._create_residents_networked()

        # DataFrame to store daily metrics
        self.metrics_df = pd.DataFrame(columns=[
            'day', 'demand', 'spoilage', 'revenue', 'satisfaction',
            'price', 'complexity_entropy', 'network_density', 'cv', 'stability_index'
        ])

        # Cache interaction matrix for performance
        self.cached_interaction_matrix = None

    # ==========================================================
    # Agent Creation and Network Initialization
    # ==========================================================
    def _create_residents_networked(self):
        """
        Create resident agents embedded in a small-world social network.
        This simulates information sharing and influence within communities.
        """
        residents = []
        G = nx.watts_strogatz_graph(n=self.num_residents, k=6, p=0.2)

        for i in range(self.num_residents):
            household_size = np.random.choice([1, 2, 3, 4])
            income_level = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
            location = (np.random.uniform(0, 10), np.random.uniform(0, 10))

            resident = ResidentAgent(
                unique_id=i + 2,
                model=self,
                household_size=household_size,
                income_level=income_level,
                location=location
            )
            resident.neighbors = list(G.neighbors(i))
            residents.append(resident)
        return residents

    # ==========================================================
    # Simulation Logic
    # ==========================================================
    def run_one_day(self):
        """
        Run one day of simulation, including:
        - Resident decision making
        - Group leader negotiation
        - Supermarket operations
        - Complexity and stability updates
        """
        daily_data = {'demand': 0, 'spoilage': 0, 'revenue': 0, 'satisfaction': 0}
        satisfaction_sum = 0

        # === Resident decision-making ===
        for resident in self.residents:
            resident.step()
            choice = resident.make_purchase_decision(
                supermarket_price=self.supermarket.base_price,
                groupbuy_price=self.leader.negotiated_price if self.leader else None
            )

            # Demand contribution based on channel choice
            if choice == "supermarket":
                daily_data['demand'] += resident.calculate_demand()
            elif choice == "groupbuy" and self.leader:
                daily_data['demand'] += resident.calculate_demand() * 0.9  # discount efficiency
            satisfaction_sum += resident.satisfaction_level

        daily_data['satisfaction'] = satisfaction_sum / len(self.residents)

        # === Group leader and supermarket ===
        if self.leader:
            self.leader.step()
        self.supermarket.step()

        # === Environmental shock and seasonal adjustment ===
        shock_multiplier = self.environment.get_demand_multiplier()
        daily_data['demand'] *= shock_multiplier

        # === Spoilage and revenue from supermarket ===
        daily_data['spoilage'] = self.supermarket.total_spoilage
        daily_data['revenue'] = self.supermarket.revenue

        # === Dynamic price feedback (supply-demand adjustment) ===
        price_adjustment = 0.01 * np.sign(daily_data['demand'] - 1000)
        self.supermarket.base_price *= (1 + price_adjustment)
        daily_data['price'] = self.supermarket.base_price

        # === Update complexity and stability metrics ===
        complexity = self._update_complexity_metrics(daily_data['demand'], daily_data['spoilage'])
        stability_index = self.calculate_system_stability()

        # === Record daily results ===
        self.metrics_df.loc[len(self.metrics_df)] = [
            self.current_day, daily_data['demand'], daily_data['spoilage'],
            daily_data['revenue'], daily_data['satisfaction'],
            daily_data['price'], complexity.get('entropy', 0),
            complexity.get('network_density', 0), complexity.get('cv', 0),
            stability_index
        ]

        # Advance to next day
        self.current_day += 1
        self.environment.advance_day()

    # ==========================================================
    # Complexity Metrics
    # ==========================================================
    def _update_complexity_metrics(self, demand, spoilage):
        """
        Update system-level complexity indicators based on:
        - Demand and spoilage series
        - Agent interaction network
        """
        if self.cached_interaction_matrix is None:
            self.cached_interaction_matrix = self._build_interaction_matrix()

        self.complexity_tracker.update_all_metrics(
            demand_series=self.metrics_df['demand'].tolist() + [demand],
            spoilage_series=self.metrics_df['spoilage'].tolist() + [spoilage],
            interaction_matrix=self.cached_interaction_matrix
        )

        return self.complexity_tracker.get_current_metrics()

    def _build_interaction_matrix(self):
        """
        Construct an interaction matrix based on the resident social network.
        Includes resident-resident, resident-leader, and leader-supermarket connections.
        """
        n_agents = len(self.residents) + 2
        matrix = np.zeros((n_agents, n_agents))

        # Resident social connections
        for r in self.residents:
            for neighbor in getattr(r, 'neighbors', []):
                matrix[r.unique_id - 2, neighbor] = 1
                matrix[neighbor, r.unique_id - 2] = 1

        # Group leader partial connectivity
        if self.leader:
            leader_idx = len(self.residents) + 1
            connected_residents = np.random.choice(
                range(len(self.residents)), size=int(0.3 * len(self.residents)), replace=False
            )
            for i in connected_residents:
                matrix[i, leader_idx] = 1
                matrix[leader_idx, i] = 1
        return matrix

    # ==========================================================
    # Stability and Trend Analysis
    # ==========================================================
    def calculate_system_stability(self):
        """
        Compute a simplified stability index.
        Defined as the inverse of total fluctuation in demand and spoilage.
        Higher values indicate greater stability.
        """
        if len(self.metrics_df) < 5:
            return 0
        demand_std = self.metrics_df['demand'].std()
        spoilage_std = self.metrics_df['spoilage'].std()
        return 1 / (demand_std + spoilage_std + 1e-6)

    def calculate_complexity_trend(self):
        """
        Calculate the trend (growth rate) of complexity indicators
        using linear regression over a sliding 30-day window.
        """
        if len(self.metrics_df) < 10:
            return {}
        trends = {}
        for metric in ['complexity_entropy', 'network_density', 'cv']:
            series = self.metrics_df[metric].dropna().values[-30:]
            if len(series) > 5:
                slope, _, _, _, _ = linregress(range(len(series)), series)
                trends[metric + '_trend'] = slope
        return trends

    # ==========================================================
    # Main Simulation
    # ==========================================================
    def run_simulation(self, days=90):
        """
        Run the full simulation for the specified number of days.
        Includes random environmental shocks every 30 days.
        """
        for _ in range(days):
            self.run_one_day()

            # Apply random external shocks occasionally
            if self.current_day % 30 == 0 and np.random.random() < 0.3:
                shock_type = np.random.choice(['demand_spike', 'supply_chain_disruption'])
                self.environment.apply_external_shock(shock_type, magnitude=0.3)

        return self.metrics_df

    def get_final_metrics(self):
        """
        Summarize final results including:
        - Average demand, spoilage, satisfaction
        - Final price
        - System stability index
        - Complexity trends
        """
        complexity_trend = self.calculate_complexity_trend()
        return {
            'avg_demand': self.metrics_df['demand'].mean(),
            'avg_spoilage': self.metrics_df['spoilage'].mean(),
            'avg_satisfaction': self.metrics_df['satisfaction'].mean(),
            'final_price': self.metrics_df['price'].iloc[-1],
            'stability_index': self.calculate_system_stability(),
            'complexity_trend': complexity_trend
        }
