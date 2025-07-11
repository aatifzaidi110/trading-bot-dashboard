import pandas as pd
import numpy as np
import os

def run_backtest(df: pd.DataFrame, strategy_obj, symbol=None, save_csv=True):
    df = df.copy()
    df["Signal"] = None

    strategy = strategy_obj
    for i in range(2, len(df)):
        sliced_df = df.iloc[:i+1]
        df.at[df.index[i], "Signal"] = strategy.generate_signal(sliced_df)

    position = 0
    cash = 10000
    holdings = 0
    values = []

    for i in range(len(df)):
        price = df.iloc[i]["close"]
        signal = df.iloc[i]["Signal"]

        if signal == "BUY" and position == 0:
            holdings = cash / price
            cash = 0
            position = 1
        elif signal == "SELL" and position == 1:
            cash = holdings * price
            holdings = 0
            position = 0

        portfolio_value = cash + holdings * price
        values.append(portfolio_value)

    df["Portfolio"] = values
    final_value = values[-1]
    returns = pd.Series(values).pct_change().dropna()

    total_return = (final_value - 10000) / 10000
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if not returns.empty else 0
    rolling_max = pd.Series(values).cummax()
    drawdowns = (pd.Series(values) - rolling_max) / rolling_max
    max_dd = drawdowns.min()

    if save_csv and symbol:
        output_dir = "logs/backtests"
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(f"{output_dir}/{symbol}_backtest.csv")

    return {
        "Start": df.index[0].strftime("%Y-%m-%d"),
        "End": df.index[-1].strftime("%Y-%m-%d"),
        "Final Value": round(final_value, 2),
        "Return (%)": round(total_return * 100, 2),
        "Sharpe Ratio": round(sharpe, 2),
        "Max Drawdown (%)": round(max_dd * 100, 2)
    }
