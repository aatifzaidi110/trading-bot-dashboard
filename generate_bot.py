import os

base_dir = "trading_bot"
folders = [
    "config", "data", "execution", "strategy", "backtest", "analysis", "logs/backtests", "logs/trades", "utils"
]

# Create folders
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

# Part 2: main & data modules - this will create main.py for live + backtest flow
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

# Part 3: Order Execution & Backtesting this will create Alpaca trade execution logging to cvs and backtesting

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

# Part 4: Strategies + Comparison + Requirements

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

# RSI Strategy
rsi_py = """\
import pandas as pd

class RSIStrategy:
    def __init__(self, period=14, lower=30, upper=70):
        self.period = period
        self.lower = lower
        self.upper = upper

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        if df["RSI"].iloc[-1] < self.lower:
            return "BUY"
        elif df["RSI"].iloc[-1] > self.upper:
            return "SELL"
        return "HOLD"
"""

with open(os.path.join(base_dir, "strategy", "rsi_strategy.py"), "w") as f:
    f.write(rsi_py)

# MACD Strategy
macd_py = """\
import pandas as pd

class MACDStrategy:
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df["EMA_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["EMA_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["MACD"] = df["EMA_fast"] - df["EMA_slow"]
        df["Signal_Line"] = df["MACD"].ewm(span=self.signal, adjust=False).mean()

        if df["MACD"].iloc[-2] < df["Signal_Line"].iloc[-2] and df["MACD"].iloc[-1] > df["Signal_Line"].iloc[-1]:
            return "BUY"
        elif df["MACD"].iloc[-2] > df["Signal_Line"].iloc[-2] and df["MACD"].iloc[-1] < df["Signal_Line"].iloc[-1]:
            return "SELL"
        return "HOLD"
"""

with open(os.path.join(base_dir, "strategy", "macd_strategy.py"), "w") as f:
    f.write(macd_py)

# Bollinger Strategy
bollinger_py = """\
import pandas as pd

class BollingerStrategy:
    def __init__(self, window=20, num_std=2):
        self.window = window
        self.num_std = num_std

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        rolling_mean = df["close"].rolling(self.window).mean()
        rolling_std = df["close"].rolling(self.window).std()
        df["Upper"] = rolling_mean + (self.num_std * rolling_std)
        df["Lower"] = rolling_mean - (self.num_std * rolling_std)

        price = df["close"].iloc[-1]
        if price < df["Lower"].iloc[-1]:
            return "BUY"
        elif price > df["Upper"].iloc[-1]:
            return "SELL"
        return "HOLD"
"""

with open(os.path.join(base_dir, "strategy", "bollinger_strategy.py"), "w") as f:
    f.write(bollinger_py)

# EMA200 Strategy
ema_py = """\
import pandas as pd

class EMA200Strategy:
    def __init__(self):
        pass

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
        price = df["close"].iloc[-1]
        ema = df["EMA200"].iloc[-1]

        if price > ema:
            return "BUY"
        elif price < ema:
            return "SELL"
        return "HOLD"
"""

with open(os.path.join(base_dir, "strategy", "ema200_trend.py"), "w") as f:
    f.write(ema_py)

# Combo Strategy
combo_py = """\
import pandas as pd

class ComboStrategy:
    def __init__(self, sma_window=50, rsi_period=14, rsi_buy=35, rsi_sell=65):
        self.sma_window = sma_window
        self.rsi_period = rsi_period
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df["SMA"] = df["close"].rolling(window=self.sma_window).mean()
        price = df["close"].iloc[-1]
        sma = df["SMA"].iloc[-1]

        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        rsi = df["RSI"].iloc[-1]

        if price > sma and rsi < self.rsi_buy:
            return "BUY"
        elif price < sma and rsi > self.rsi_sell:
            return "SELL"
        return "HOLD"
"""

with open(os.path.join(base_dir, "strategy", "combo_strategy.py"), "w") as f:
    f.write(combo_py)

# Ensemble Strategy
ensemble_py = """\
from strategy.rsi_strategy import RSIStrategy
from strategy.sma_crossover import SMACrossoverStrategy
from strategy.macd_strategy import MACDStrategy

class EnsembleStrategy:
    def __init__(self):
        self.strategies = [
            RSIStrategy(14, 30, 70),
            SMACrossoverStrategy(20, 50),
            MACDStrategy()
        ]

    def generate_signal(self, df):
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for strat in self.strategies:
            signal = strat.generate_signal(df)
            votes[signal] += 1

        if votes["BUY"] >= 2:
            return "BUY"
        elif votes["SELL"] >= 2:
            return "SELL"
        else:
            return "HOLD"
"""

with open(os.path.join(base_dir, "strategy", "ensemble_strategy.py"), "w") as f:
    f.write(ensemble_py)

# Compare script
compare_py = """\
from config import settings
from data import fetch_data
from backtest import backtester

from strategy.sma_crossover import SMACrossoverStrategy
from strategy.rsi_strategy import RSIStrategy
from strategy.macd_strategy import MACDStrategy
from strategy.bollinger_strategy import BollingerStrategy
from strategy.ema200_trend import EMA200Strategy
from strategy.combo_strategy import ComboStrategy

def compare_strategies(symbol):
    df = fetch_data.get_data(symbol, settings.START_DATE, settings.END_DATE, settings.TIMEFRAME)
    if df is None or df.empty:
        print(f"No data for {symbol}")
        return

    strategies = {
        "SMA_Crossover": SMACrossoverStrategy(20, 50),
        "RSI": RSIStrategy(14, 30, 70),
        "MACD": MACDStrategy(),
        "Bollinger": BollingerStrategy(),
        "EMA200": EMA200Strategy(),
        "Combo": ComboStrategy()
    }

    results = []
    for name, strategy in strategies.items():
        result = backtester.run_backtest(df, strategy, symbol=symbol, save_csv=False)
        result["Strategy"] = name
        results.append(result)

    print(f"\\nBacktest Summary for {symbol}:\\n")
    print("{:<15} {:<12} {:<12} {:<12} {:<14} {:<18}".format(
        "Strategy", "Final Value", "Return (%)", "Sharpe", "Max Drawdown", "Period"
    ))
    for r in results:
        print("{:<15} ${:<11} {:<12} {:<12} {:<14} {} to {}".format(
            r["Strategy"], r["Final Value"], r["Return (%)"], r["Sharpe Ratio"],
            f"{r['Max Drawdown (%)']}%", r["Start"], r["End"]
        ))

if __name__ == "__main__":
    compare_strategies("AAPL")
"""

with open(os.path.join(base_dir, "analysis", "compare_strategies.py"), "w") as f:
    f.write(compare_py)

# requirements.txt
reqs = """\
pandas
numpy
requests
"""

with open(os.path.join(base_dir, "requirements.txt"), "w") as f:
    f.write(reqs)
