# utils/plot_ensemble.py

import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_ensemble_votes(csv_path="logs/ensemble_votes.csv"):
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df.sort_values("timestamp", inplace=True)

    # Plot 1: Final Signal Over Time
    signal_map = {"BUY": 1, "HOLD": 0, "SELL": -1}
    df["signal_numeric"] = df["final_signal"].map(signal_map)

    plt.figure(figsize=(12, 4))
    plt.plot(df["timestamp"], df["signal_numeric"], marker="o", linestyle="-", color="purple")
    plt.yticks([-1, 0, 1], ["SELL", "HOLD", "BUY"])
    plt.title("🧠 Final Ensemble Signal Over Time")
    plt.xlabel("Time")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot 2: Vote Breakdown (BUY/SELL/HOLD)
    plt.figure(figsize=(12, 4))
    plt.plot(df["timestamp"], df["BUY"], label="BUY", color="green", marker="o")
    plt.plot(df["timestamp"], df["SELL"], label="SELL", color="red", marker="o")
    plt.plot(df["timestamp"], df["HOLD"], label="HOLD", color="gray", marker="o")
    plt.title("📊 Ensemble Vote Weights")
    plt.xlabel("Time")
    plt.ylabel("Vote Weight")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot 3: Strategy Individual Votes (if present)
    strategies = [col.replace("_vote", "") for col in df.columns if col.endswith("_vote")]
    if strategies:
        fig, ax = plt.subplots(len(strategies), 1, figsize=(12, 2 * len(strategies)), sharex=True)
        for i, strat in enumerate(strategies):
            signal_vals = df[f"{strat}_vote"].map(signal_map)
            ax[i].plot(df["timestamp"], signal_vals, marker="o", label=strat)
            ax[i].set_title(strat)
            ax[i].set_yticks([-1, 0, 1])
            ax[i].set_yticklabels(["SELL", "HOLD", "BUY"])
            ax[i].grid(True)
        plt.tight_layout()
        plt.show()
    else:
        print("ℹ️ No individual strategy votes found in the CSV.")

if __name__ == "__main__":
    plot_ensemble_votes()