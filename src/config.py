# config.py — Global Configuration for Community Group Buying ABM

# ---- 🧠 Agent Settings ----
N_CONSUMERS = 100             # Number of consumers
N_LEADERS = 3                # Number of group leaders
LEADER_CONNECTION_RATIO = 0.3 # Ratio of consumers covered by each leader

# ---- 💰 Platform Economic Parameters ----
BASE_PRICE = 5               # Platform base price
INITIAL_SUBSIDY = 3          # Initial subsidy amount
SUBSIDY_DECAY_RATE = 0.95    # Subsidy decay rate per round

# ---- 🤝 Trust Diffusion Parameters ----
DEFAULT_TRUST_DIFFUSION = 0.05   # Trust diffusion ratio
INFLUENCE_STRENGTH = 0.3         # Leader influence strength
TRUST_GROWTH_RATE = 0.1          # Trust diffusion amplitude (word-of-mouth effect)
DIFFUSION_RATES = [0.02, 0.05, 0.1, 0.2]  # Parameter sensitivity test range

# ---- 🧮 Simulation Settings ----
STEPS = 25                   # Number of simulation rounds