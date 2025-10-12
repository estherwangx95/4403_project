# ============================================================
# utils.py — Unified Analysis and Visualization Utilities
# ============================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random, os, imageio
import networkx as nx
from model import GroupBuyingModel
import config

# ============================================================
# === 1️⃣ 核心绘图函数 ===
# ============================================================

def plot_system_dynamics(model):
    """绘制 Figure 6.3: 销售、信任、补贴三变量动态曲线"""
    steps = np.arange(len(model.sales_record))
    fig, ax1 = plt.subplots(figsize=(8,5))
    ax1.plot(steps, model.sales_record, 'o-', color=config.PLOT_COLORS["sales"], label="Total Sales")
    ax1.set_xlabel("Time Step")
    ax1.set_ylabel("Total Sales", color=config.PLOT_COLORS["sales"])

    ax2 = ax1.twinx()
    ax2.plot(steps, model.avg_trust_record, '--', color=config.PLOT_COLORS["trust"], label="Average Trust")
    ax2.plot(steps, model.subsidy_record, '-.', color=config.PLOT_COLORS["subsidy"], label="Platform Subsidy")
    plt.title("Figure 6.3: Temporal Dynamics of Sales, Trust, and Subsidy")

    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.grid(True)
    plt.show()


def export_data(model):
    """导出模型结果为 CSV"""
    df = pd.DataFrame({
        "step": np.arange(len(model.sales_record)),
        "sales": model.sales_record,
        "avg_trust": model.avg_trust_record,
        "subsidy": model.subsidy_record
    })
    os.makedirs(config.SAVE_PATH, exist_ok=True)
    file_path = os.path.join(config.SAVE_PATH, config.EXPORT_CSV)
    df.to_csv(file_path, index=False)
    print(f"✅ Data exported to {file_path}")


# ============================================================
# === 2️⃣ 模型验证与敏感性分析 ===
# ============================================================

def run_stability_test():
    """Figure 6.4 稳定性验证"""
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
    plt.xlabel("Time Step")
    plt.ylabel("Sales")
    plt.legend()
    plt.grid(True)
    plt.show()


def run_parameter_sensitivity():
    """Figure 6.5 参数敏感性测试"""
    plt.figure(figsize=(8,5))
    results = []
    for rate in config.DIFFUSION_RATES:
        model = GroupBuyingModel(config.N_CONSUMERS, config.N_LEADERS)
        for c in model.consumers:
            c.diffusion_rate = rate
        for _ in range(config.STEPS):
            model.step()
        plt.plot(model.avg_trust_record, label=f"rate={rate}")
        results.append([rate, model.avg_trust_record[-1]])

    plt.title("Figure 6.5: Sensitivity of Trust Diffusion Rate")
    plt.xlabel("Time Step")
    plt.ylabel("Average Trust")
    plt.legend()
    plt.grid(True)
    plt.show()

    df = pd.DataFrame(results, columns=["Diffusion Rate", "Final Avg Trust"])
    print("\n📊 Final Average Trust by Diffusion Rate:")
    print(df.to_string(index=False))


# ============================================================
# === 3️⃣ 动态信任传播可视化 ===
# ============================================================

def save_trust_diffusion_gif(model, filename=None):
    """生成信任传播 GIF 动画"""
    os.makedirs(config.SAVE_PATH, exist_ok=True)
    filename = filename or config.GIF_NAME
    gif_path = os.path.join(config.SAVE_PATH, filename)

    images = []
    for step in range(config.STEPS):
        trust_values = [c.trust for c in model.consumers]
        plt.figure(figsize=(6,5))
        plt.scatter(range(len(trust_values)), trust_values, c=trust_values, cmap="plasma", s=60)
        plt.title(f"Trust Diffusion Step {step+1}")
        plt.xlabel("Consumers")
        plt.ylabel("Trust Level")
        plt.colorbar(label="Trust")
        plt.tight_layout()
        plt.savefig("temp.png")
        plt.close()
        images.append(imageio.imread("temp.png"))
    imageio.mimsave(gif_path, images, fps=2)
    os.remove("temp.png")
    print(f"🎞️ GIF saved at {gif_path}")


# ============================================================
# === 4️⃣ 双视图信任网络可视化 ===
# ============================================================

def save_trust_diffusion_and_evolution_gif(model, filename="trust_diffusion_evolution_fixed.gif"):
    """
    🎞️ 修正版：同时展示信任扩散网络 + 平均信任动态演化
    修复点：
      ✅ 每帧更新模型状态
      ✅ 动态绘制平均信任曲线（累积）
      ✅ 网络节点颜色与曲线联动
    """
    os.makedirs(config.SAVE_PATH, exist_ok=True)
    gif_path = os.path.join(config.SAVE_PATH, filename)

    # 固定网络结构布局（模拟邻里关系）
    n = len(model.consumers)
    G = nx.erdos_renyi_graph(n, 0.1)
    pos = nx.spring_layout(G, seed=42)

    images = []
    avg_trust_values = []

    for step in range(config.STEPS):
        # === 强制更新模型状态 ===
        model.step()

        # === 获取当前信任信息 ===
        trust_values = np.array([c.trust for c in model.consumers])
        avg_trust = np.mean(trust_values)
        avg_trust_values.append(avg_trust)

        # === 绘制双视图 ===
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))

        # ---- 左图：网络信任扩散 ----
        nx.draw(
            G,
            pos,
            node_color=trust_values,
            cmap="plasma",
            node_size=150,
            edge_color="lightgray",
            ax=axes[0],
        )
        axes[0].set_title(f"Trust Diffusion Network — Step {step+1}")
        axes[0].axis("off")

        # ---- 右图：平均信任演化 ----
        axes[1].plot(avg_trust_values, color="red", linewidth=2.5)
        axes[1].set_xlim(0, config.STEPS)
        axes[1].set_ylim(0.4, 1)
        axes[1].set_title("Average Trust Evolution")
        axes[1].set_xlabel("Time Step")
        axes[1].set_ylabel("Average Trust")
        axes[1].grid(True)

        # ✅ 显示当前信任数值
        axes[1].text(
            len(avg_trust_values) - 1,
            avg_trust_values[-1] + 0.02,
            f"{avg_trust_values[-1]:.2f}",
            color="black",
            fontsize=9,
        )

        # 保存临时帧
        tmp_path = os.path.join(config.SAVE_PATH, "frame_temp.png")
        plt.tight_layout()
        plt.savefig(tmp_path)
        plt.close()
        images.append(imageio.imread(tmp_path))

    # === 导出GIF ===
    imageio.mimsave(gif_path, images, fps=2)
    os.remove(tmp_path)
    print(f"🎬 Fixed dual-view GIF saved at: {gif_path}")