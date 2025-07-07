# utils/dashboard_generator.py

import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_dashboard():
    log_path = os.path.join("logs", "performance", "strategy_performance_log.csv")

    if not os.path.exists(log_path):
        print("❌ No performance log found.")
        return

    df = pd.read_csv(log_path)

    if df.empty:
        print("⚠️ Performance log is empty.")
        return

    plt.style.use("seaborn-darkgrid")
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("📊 Strategy Performance Dashboard", fontsize=16)

    df.groupby("Symbol")["Return (%)"].mean().plot.bar(ax=axs[0, 0], color="green", title="Avg Return (%) by Symbol")
    df.groupby("Symbol")["Sharpe Ratio"].mean().plot.bar(ax=axs[0, 1], color="blue", title="Avg Sharpe Ratio")
    df.groupby("Symbol")["Max Drawdown (%)"].min().plot.bar(ax=axs[1, 0], color="red", title="Worst Drawdown (%)")
    df["Strategy"].value_counts().plot.pie(ax=axs[1, 1], autopct="%1.1f%%", title="Run Count per Strategy")

    for ax in axs.flat:
        ax.set_ylabel("")
        ax.set_xlabel("")

    plt.tight_layout()
    output_path = os.path.join("logs", "performance", "dashboard.png")
    plt.savefig(output_path)
    print(f"✅ Dashboard saved to: {output_path}")