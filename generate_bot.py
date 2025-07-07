import os

base_dir = "trading_bot"
folders = [
    "config", "data", "execution", "strategy", "backtest", "analysis",
    "logs/backtests", "logs/trades", "utils"
]

# Create folder structure
for folder in folders:
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

# ──────────────────────────────────────────────────────
# config/settings.py
settings_py = """\
ALPACA_API_KEY = "YOUR_ALPACA_API_KEY"
ALPACA_SECRET_KEY = "YOUR_ALPACA_SECRET_KEY"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

SYMBOLS = ["AAPL", "MSFT", "TSLA"]
TIMEFRAME = "1D"
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
INITIAL_CAPITAL = 10000

SMA_SHORT_WINDOW = 20
SMA_LONG_WINDOW = 50
"""

with open(os.path.join(base_dir, "config", "settings.py"), "w") as f:
    f.write(settings_py)

# ──────────────────────────────────────────────────────
# utils/logger.py
logger_py = """\
import logging

def setup_logger(name='bot_logger'):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
"""

with open(os.path.join(base_dir, "utils", "logger.py"), "w") as f:
    f.write(logger_py)

# ──────────────────────────────────────────────────────
# main.py
main_py = """\
from config import settings
from data import fetch_data
from strategy.sma_crossover import SMACrossoverStrategy
from execution import order_manager
from backtest import backtester
from utils.logger import setup_logger

logger = setup_logger()

def process_symbol(symbol):
    logger.info(f"Processing {symbol}...")
    df = fetch_data.get_data(symbol, settings.START_DATE, settings.END_DATE, settings.TIMEFRAME)
    if df is None or df.empty:
        logger.warning(f"No data for {symbol}")
        return

    strategy = SMACrossoverStrategy(
        short_window=settings.SMA_SHORT_WINDOW,
        long_window=settings.SMA_LONG_WINDOW
    )

    results = backtester.run_backtest(df, strategy, symbol)
    logger.info(f"{symbol} Backtest Results: {results}")

    signal = strategy.generate_signal(df)
    order_manager.execute_trade(symbol, signal)

def main():
    logger.info("Trading Bot Starting...")
    for symbol in settings.SYMBOLS:
        try:
            process_symbol(symbol)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")

if __name__ == "__main__":
    main()
"""

with open(os.path.join(base_dir, "main.py"), "w") as f:
    f.write(main_py)

# ──────────────────────────────────────────────────────
# data/fetch_data.py
fetch_data_py = """\
import requests
import pandas as pd
from config import settings

def get_data(symbol, start_date, end_date, timeframe):
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/bars"
    headers = {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
    }
    params = {
        "start": start_date,
        "end": end_date,
        "timeframe": timeframe,
        "limit": 10000
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        bars = response.json().get("bars", [])
        if not bars:
            return None

        df = pd.DataFrame(bars)
        df['t'] = pd.to_datetime(df['t'])
        df.set_index('t', inplace=True)
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True)
        return df

    except Exception as e:
        print(f"Failed to fetch data for {symbol}: {e}")
        return None
"""

with open(os.path.join(base_dir, "data", "fetch_data.py"), "w") as f:
    f.write(fetch_data_py)

# ──────────────────────────────────────────────────────
# execution/order_manager.py
order_manager_py = """\
import requests
from datetime import datetime
import csv
import os
from config import settings
from utils.logger import setup_logger

logger = setup_logger()

def execute_trade(symbol, signal):
    if signal not in ("BUY", "SELL"):
        logger.info(f"{symbol}: No trade executed (signal: {signal})")
        return

    side = "buy" if signal == "BUY" else "sell"

    url = f"{settings.ALPACA_BASE_URL}/v2/orders"
    headers = {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "symbol": symbol,
        "qty": 1,
        "side": side,
        "type": "market",
        "time_in_force": "gtc"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        order_data = response.json()
        logger.info(f"Executed {side.upper()} order for {symbol}: {order_data['id']}")
        _log_trade(symbol, signal, order_data['id'])
    except Exception as e:
        logger.error(f"Trade execution failed for {symbol}: {e}")

def _log_trade(symbol, signal, order_id):
    log_dir = "logs/trades"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "executed_trades.csv")
    log_exists = os.path.isfile(log_file)

    with open(log_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not log_exists:
            writer.writerow(["timestamp", "symbol", "signal", "order_id"])
        writer.writerow([datetime.now().isoformat(), symbol, signal, order_id])
"""

with open(os.path.join(base_dir, "execution", "order_manager.py"), "w") as f:
    f.write(order_manager_py)

# ──────────────────────────────────────────────────────
# backtest/backtester.py
backtester_py = """\
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
"""

with open(os.path.join(base_dir, "backtest", "backtester.py"), "w") as f:
    f.write(backtester_py)

# ──────────────────────────────────────────────────────
# strategy/sma_crossover.py
sma_py = """\
import pandas as pd

class SMACrossoverStrategy:
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df['SMA_Short'] = df['close'].rolling(window=self.short_window).mean()
        df['SMA_Long'] = df['close'].rolling(window=self.long_window).mean()

        if df['SMA_Short'].iloc[-2] < df['SMA_Long'].iloc[-2] and df['SMA_Short'].iloc[-1] > df['SMA_Long'].iloc[-1]:
            return "BUY"
        elif df['SMA_Short'].iloc[-2] > df['SMA_Long'].iloc[-2] and df['SMA_Short'].iloc[-1] < df['SMA_Long'].iloc[-1]:
            return "SELL"
        return "HOLD"
"""

with open(os.path.join(base_dir, "strategy", "sma_crossover.py"), "w") as f:
    f.write(sma_py)

# ──────────────────────────────────────────────────────
# requirements.txt
reqs = """\
pandas
numpy
requests
"""

with open(os.path.join(base_dir, "requirements.txt"), "w") as f:
    f.write(reqs)

print("✅ Project structure generated successfully.")
