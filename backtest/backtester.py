# backtest/backtester.py

import pandas as pd
from core.utils.data_loader import load_data
import matplotlib.pyplot as plt

def run_backtest(strategy, symbol, period="6mo", interval="1d", plot=True):
    df = load_data(symbol, period=period, interval=interval)
    if df is None or df.empty:
        raise ValueError(f"No data loaded for {symbol}")

    result_df = strategy.generate_signals(df)
    summary = strategy.get_performance_summary()

    print(f"\n📊 Backtest Results for {symbol} using {strategy.name}:")
    print(f"Trades: {summary['total_trades']}")
    print(f"Wins: {summary['wins']}, Losses: {summary['losses']}")
    print(f"Win Rate: {summary['win_rate'] * 100:.2f}%")
    print(f"Total Return: {summary['Return (%)']}%")

    if plot:
        _plot_signals(result_df, symbol)

    return summary

def _plot_signals(df: pd.DataFrame, symbol: str):
    import matplotlib.dates as mdates

    buy_signals = df[df["Signal"] == "BUY"]
    exit_signals = df[df["Signal"].isin(["TAKE_PROFIT", "STOP_LOSS"])]

    plt.figure(figsize=(14, 6))
    plt.plot(df["close"], label="Price", linewidth=1)
    plt.scatter(buy_signals.index, buy_signals["close"], marker="^", color="green", label="BUY")
    plt.scatter(exit_signals.index, exit_signals["close"], marker="v", color="red", label="SELL")
    plt.title(f"{symbol} - Strategy Signals")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
