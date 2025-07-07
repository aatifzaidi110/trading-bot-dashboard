# strategy/bollinger_strategy.py

import pandas as pd
import logging
from core.utils.performance_tracker import PerformanceTracker
from core.logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class BollingerStrategy:
    def __init__(self, window=20, num_std_dev=2, name="BollingerStrategy"):
        self.window = window
        self.num_std_dev = num_std_dev
        self.name = name
        self.tracker = PerformanceTracker(self.name)
        self.enabled = True
        self.min_win_rate_threshold = 0.3

    def generate_signals(self, df):
        if not self.enabled:
            logger.info(f"🚫 Strategy {self.name} is paused.")
            df["Signal"] = "HOLD"
            return df

        df = df.copy()
        df["ma"] = df["close"].rolling(window=self.window).mean()
        df["std"] = df["close"].rolling(window=self.window).std()
        df["upper"] = df["ma"] + self.num_std_dev * df["std"]
        df["lower"] = df["ma"] - self.num_std_dev * df["std"]
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df["Signal"] = "HOLD"

        position = None
        entry_price = None

        for i in range(len(df)):
            row = df.iloc[i]
            price = row["close"]

            if position is None and price < row["lower"]:
                df.at[i, "Signal"] = "BUY"
                position = "LONG"
                entry_price = price
                log_trade(df.index[i], price, "BUY", "LONG", entry_price)

            elif position == "LONG" and price > row["ma"]:
                df.at[i, "Signal"] = "SELL"
                log_trade(df.index[i], price, "SELL", "LONG", entry_price)
                self.tracker.record_trade("WIN" if price > entry_price else "LOSS")
                position = None
                entry_price = None

        self.adapt_parameters()
        return df

    def generate_signal(self, df):
        df = self.generate_signals(df)
        if df.empty or "Signal" not in df.columns:
            return "HOLD"
        return df["Signal"].iloc[-1]

    def adapt_parameters(self):
        summary = self.tracker.get_performance_summary()
        if summary["total_trades"] >= 5 and summary["win_rate"] < self.min_win_rate_threshold:
            logger.warning(f"?? Pausing {self.name} due to low win rate = {summary['win_rate']:.2f}")
            self.enabled = False


    def performance_summary(self):
        return self.tracker.get_performance_summary()
