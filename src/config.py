# ============================================================
# config.py — Global Configuration for Community Group Buying ABM
# ============================================================

# ---- 🧠 Agent Settings ----
N_CONSUMERS = 50             # 消费者数量
N_LEADERS = 3                # 团长数量
LEADER_CONNECTION_RATIO = 0.3 # 每个团长覆盖的消费者比例

# ---- 💰 Platform Economic Parameters ----
BASE_PRICE = 5               # 平台基础价格
INITIAL_SUBSIDY = 3          # 初始补贴金额
SUBSIDY_DECAY_RATE = 0.95    # 每轮补贴衰减率

# ---- 🤝 Trust Diffusion Parameters ----
DEFAULT_TRUST_DIFFUSION = 0.05   # 信任传播比例
INFLUENCE_STRENGTH = 0.3         # 团长影响力强度
TRUST_GROWTH_RATE = 0.1          # 信任传播幅度（口碑效应）
DIFFUSION_RATES = [0.02, 0.05, 0.1, 0.2]  # ← 新增：参数敏感性实验的测试范围

# ---- 🧮 Simulation Settings ----
STEPS = 25                   # 模拟轮数
RUNS = 5                     # 稳定性实验重复次数
RANDOM_SEEDS = [10, 20, 30, 40, 50]

# ---- 🎨 Visualization Settings ----
SAVE_PATH = "../data/"
GIF_NAME = "trust_diffusion.gif"
EXPORT_CSV = "validation_output.csv"
PLOT_COLORS = {
    "sales": "b",
    "trust": "r",
    "subsidy": "g"
}

# ---- 🔧 Experiment Flags ----
VERBOSE = True                # 是否输出每步日志