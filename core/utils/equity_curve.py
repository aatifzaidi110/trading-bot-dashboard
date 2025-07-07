# utils/equity_curve.py

import matplotlib.pyplot as plt
import os

def save_equity_curve(symbol, equity_df):
    if "Equity" not in equity_df.columns:
        raise ValueError("DataFrame must contain 'Equity' column")

    plt.figure(figsize=(10, 5))
    plt.plot(equity_df["Date"], equity_df["Equity"], label="Equity Curve")
    plt.title(f"{symbol} Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.grid(True)
    plt.legend()

    output_dir = "logs/backtests"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{symbol}_equity_curve.png")
    plt.savefig(filepath)
    plt.close()