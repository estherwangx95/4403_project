import numpy as np

class ComplexityMetrics:
    """
    System metrics
    --------------
    Tracks entropy, variation, and network density to quantify
    system volatility and coordination level.
    """

    def __init__(self):
        self.history = {
            "entropy": [],
            "cv": [],
            "network_density": []
        }

    # ------------------------------------------------------------
    def entropy(self, data):
        """Shannon entropy of a numeric series."""
        if len(data) < 2:
            return 0.0
        hist, _ = np.histogram(data, bins=10, density=True)
        hist = hist[hist > 0]
        return float(-np.sum(hist * np.log2(hist))) if len(hist) else 0.0

    # ------------------------------------------------------------
    def variation_coefficient(self, data):
        """Coefficient of variation (std / mean)."""
        mean = np.mean(data)
        return float(np.std(data) / mean) if len(data) > 1 and mean != 0 else 0.0

    # ------------------------------------------------------------
    def network_density(self, matrix):
        """Proportion of active links among all possible pairs."""
        if matrix.size == 0:
            return 0.0
        n = len(matrix)
        active = np.sum(matrix > 0)
        possible = n * (n - 1)
        return float(active / possible) if possible > 0 else 0.0

    # ------------------------------------------------------------
    def update(self, demand_series, spoilage_series, interaction_matrix):
        """Compute and record current metrics."""
        combined = np.array(demand_series) + np.array(spoilage_series)

        self.history["entropy"].append(self.entropy(combined))
        self.history["cv"].append(self.variation_coefficient(combined))
        self.history["network_density"].append(self.network_density(interaction_matrix))

    # ------------------------------------------------------------
    def latest(self):
        """Return the most recent metric values."""
        return {k: (v[-1] if v else 0.0) for k, v in self.history.items()}
