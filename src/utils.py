import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import imageio
import sys, os
import networkx as nx
from model import GroupBuyingModel
import config


# ============================================================
# === 1️⃣ 核心绘图函数 ===
# ============================================================

def plot_system_dynamics(model):
    """绘制 Figure 6.3：销量、信任、补贴三变量动态曲线"""
    steps = np.arange(len(model.sales_record))
    fig, ax1 = plt.subplots(figsize=(8,5))
    ax1.plot(steps, model.sales_record, 'o-', color='b', label="Total Sales")
    ax1.set_xlabel("Time Step")
    ax1.set_ylabel("Total Sales", color='b')
    ax2 = ax1.twinx()
    ax2.plot(steps, model.avg_trust_record, '--', color='r', label="Average Trust")
    ax2.plot(steps, model.subsidy_record, '-.', color='g', label="Platform Subsidy")
    plt.title("Figure 6.3: Temporal Dynamics of Sales, Trust, and Subsidy")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.grid(True)
    plt.show()


def export_data(model):
    """导出模型数据为 CSV 文件"""
    df = pd.DataFrame({
        "step": np.arange(len(model.sales_record)),
        "sales": model.sales_record,
        "avg_trust": model.avg_trust_record,
        "subsidy": model.subsidy_record
    })
    path = os.path.join(config.SAVE_PATH, config.EXPORT_CSV)
    os.makedirs(config.SAVE_PATH, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"✅ Simulation data exported to {path}")


# ============================================================
# === 2️⃣ 模型实验函数 ===
# ============================================================

def run_base_validation():
    """运行基本验证实验"""
    model = GroupBuyingModel(
        n_consumers=config.N_CONSUMERS,
        n_leaders=config.N_LEADERS,
        base_price=config.BASE_PRICE,
        subsidy=config.INITIAL_SUBSIDY
    )
    for _ in range(config.STEPS):
        model.step()
    plot_system_dynamics(model)
    export_data(model)
    return model


def run_stability_test():
    """多随机种子稳定性验证 (Figure 6.4)"""
    all_runs = []
    for seed in config.RANDOM_SEEDS[:config.RUNS]:
        random.seed(seed)
        model = GroupBuyingModel(config.N_CONSUMERS, config.N_LEADERS)
        for _ in range(config.STEPS):
            model.step()
        all_runs.append(model.sales_record)

    avg_sales = np.mean(all_runs, axis=0)
    plt.figure(figsize=(8,5))
    for i, r in enumerate(all_runs):
        plt.plot(r, alpha=0.3, label=f"Run {i+1}")
    plt.plot(avg_sales, "k--", linewidth=2.5, label="Average")
    plt.title("Figure 6.4: Stability Across Random Seeds")
    plt.xlabel("Time step")
    plt.ylabel("Sales")
    plt.legend()
    plt.grid(True)
    plt.show()


def run_parameter_sensitivity():
    """参数敏感性测试 (Figure 6.5)"""
    plt.figure(figsize=(8,5))
    for rate in config.DIFFUSION_RATES:
        model = GroupBuyingModel(config.N_CONSUMERS, config.N_LEADERS)
        for c in model.consumers:
            c.diffusion_rate = rate
        for _ in range(config.STEPS):
            model.step()
        plt.plot(model.avg_trust_record, label=f"rate={rate}")
    plt.title("Figure 6.5: Sensitivity of Trust Diffusion Rate")
    plt.xlabel("Time Step")
    plt.ylabel("Average Trust")
    plt.legend()
    plt.grid(True)
    plt.show()


# ============================================================
# === 3️⃣ 动态可视化函数 ===
# ============================================================

def save_trust_diffusion_gif(model):
    """生成信任传播 GIF 动画"""
    images = []
    for step, trust_values in enumerate([[c.trust for c in model.consumers]]):
        plt.figure(figsize=(6,5))
        plt.scatter(range(len(trust_values)), trust_values, c=trust_values, cmap="plasma")
        plt.title(f"Trust Diffusion Step {step+1}")
        plt.xlabel("Consumers")
        plt.ylabel("Trust Level")
        plt.colorbar(label="Trust")
        plt.savefig("temp.png")
        plt.close()
        images.append(imageio.imread("temp.png"))
    gif_path = os.path.join(config.SAVE_PATH, config.GIF_NAME)
    imageio.mimsave(gif_path, images, fps=2)
    os.remove("temp.png")
    print(f"🎞️ GIF saved at {gif_path}")


def plot_dual_trust_diffusion(model):
    """绘制双视图信任网络扩散"""
    G = nx.erdos_renyi_graph(len(model.consumers), 0.1)
    trust_values = [c.trust for c in model.consumers]
    plt.figure(figsize=(8,5))
    nx.draw(G, node_color=trust_values, cmap="plasma", node_size=120, with_labels=False)
    plt.title("Dual View: Network Trust Diffusion")
    plt.show()