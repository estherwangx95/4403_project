# ============================================================
# utils.py — Unified analysis & visualization utilities
# Supports Figure 6.3, 6.4, 6.5 auto-save
# ============================================================

import os, datetime, random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import imageio.v2 as imageio
import config
from model import GroupBuyingModel

# === 创建 data 目录 ===
DATA_DIR = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# 🔹 通用保存函数
# ============================================================
def save_figure(fig, name_prefix):
    """Save figure with timestamp under /data/ directory"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(DATA_DIR, f"{name_prefix}_{timestamp}.png")
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"💾 Figure saved to: {filepath}")
    return filepath


# ============================================================
# 🔹 Figure 6.3: System Dynamics Plot
# ============================================================
def plot_system_dynamics(model):
    """Plot the temporal evolution of sales, trust, and subsidy"""
    steps = range(len(model.sales_record))
    sales = model.sales_record
    trust = model.avg_trust_record
    subsidy = model.subsidy_record

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.set_title("Figure 6.3: Temporal Dynamics of Sales, Trust, and Subsidy", fontsize=12, weight='bold')
    ax1.plot(steps, sales, 'o-', color='blue', label='Total Sales')
    ax1.set_xlabel("Time Step")
    ax1.set_ylabel("Total Sales", color='blue')

    ax2 = ax1.twinx()
    ax2.plot(steps, trust, 'r--', label='Average Trust')
    ax2.plot(steps, subsidy, 'g-.', label='Platform Subsidy')
    ax2.set_ylabel("Trust / Subsidy")

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='best')

    fig.tight_layout()
    save_figure(fig, "Figure_6_3_Temporal_Dynamics")
    return fig


# ============================================================
# 🔹 Figure 6.4: Stability Test
# ============================================================
def run_stability_test(n_runs=5):
    """Run multiple independent simulations to verify stability"""
    print(f"🔁 Running {n_runs} stability simulations...")
    all_sales = []

    for i in range(n_runs):
        model = GroupBuyingModel()
        for _ in range(config.STEPS):
            model.step()
        all_sales.append(model.sales_record)

    avg_sales = np.mean(all_sales, axis=0)
    std_sales = np.std(all_sales, axis=0)
    steps = range(config.STEPS)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title("Figure 6.4: Stability Test (Sales Across Multiple Runs)", fontsize=12, weight='bold')
    for run in all_sales:
        ax.plot(steps, run, color='lightgray', alpha=0.6)
    ax.plot(steps, avg_sales, color='blue', label='Average Sales', linewidth=2)
    ax.fill_between(steps, avg_sales - std_sales, avg_sales + std_sales, color='blue', alpha=0.2)
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Total Sales")
    ax.legend()

    fig.tight_layout()
    save_figure(fig, "Figure_6_4_Stability_Test")
    return fig


# ============================================================
# 🔹 Figure 6.5: Parameter Sensitivity
# ============================================================
def run_parameter_sensitivity():
    """Parameter sensitivity test for trust diffusion rate"""
    print("🔍 Running parameter sensitivity analysis...")

    diffusion_rates = getattr(config, "DIFFUSION_RATES", [0.01, 0.02, 0.05, 0.1])
    results = []

    fig, ax = plt.subplots(figsize=(8, 5))
    for rate in diffusion_rates:
        config.TRUST_GROWTH_RATE = rate
        model = GroupBuyingModel()
        for _ in range(config.STEPS):
            model.step()
        avg_trust = np.mean(model.avg_trust_record)
        results.append((rate, avg_trust))
        ax.plot(range(len(model.avg_trust_record)), model.avg_trust_record, label=f"Rate={rate}")

    ax.set_title("Figure 6.5: Parameter Sensitivity (Trust Diffusion Rate)", fontsize=12, weight='bold')
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Average Trust")
    ax.legend()

    fig.tight_layout()
    save_figure(fig, "Figure_6_5_Parameter_Sensitivity")

    df = pd.DataFrame(results, columns=["Diffusion Rate", "Final Avg Trust"])
    csv_path = os.path.join(DATA_DIR, "parameter_sensitivity.csv")
    df.to_csv(csv_path, index=False)
    print(f"📊 Sensitivity data saved to: {csv_path}")

    return fig


# ============================================================
# 🔹 Export Data
# ============================================================
def export_data(model):
    """Export simulation records as CSV"""
    df = pd.DataFrame({
        "sales": model.sales_record,
        "avg_trust": model.avg_trust_record,
        "subsidy": model.subsidy_record
    })
    csv_path = os.path.join(DATA_DIR, "simulation_records.csv")
    df.to_csv(csv_path, index=False)
    print(f"📂 Simulation data exported to: {csv_path}")
    return csv_path