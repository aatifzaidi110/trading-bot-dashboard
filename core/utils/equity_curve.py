# core/utils/equity_curve.py

import os
import pandas as pd
import matplotlib.pyplot as plt

def save_equity_curve(symbol, equity_df):
    """
    Save the equity curve as a PNG file for the given symbol.
    """
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


def load_equity_curves(symbols):
    """
    Load equity curves from CSV files for the given list of symbols.

    Args:
        symbols (list[str]): List of ticker symbols.

    Returns:
        pd.DataFrame: Combined equity curve DataFrame with a 'Date' column.
    """
    curves = []
    for symbol in symbols:
        path = os.path.join("data", "equity_curves", f"{symbol}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["Date"])
            df["Symbol"] = symbol
            curves.append(df)

    return pd.concat(curves, ignore_index=True) if curves else pd.DataFrame()
