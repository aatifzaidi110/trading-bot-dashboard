# strategy/sma_crossover.py

import pandas as pd
import logging
from utils.performance_tracker import PerformanceTracker
from logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class SMACrossoverStrategy:
    def __init__(self, fast=20, slow=50, name="SMACrossoverStrategy"):
        self.fast = fast
        self.slow = slow
        self.name = name
        self.tracker = PerformanceTracker(self.name)
        self.enabled = True
        self.min_win_rate_threshold = 0.3

    def generate_signals(self, df):
        if not self.enabled:
            logger.info(f"?? Strategy {self.name} is paused.")
            df["Signal"] = "HOLD"
            return df

        df = df.copy()
        df["sma_fast"] = df["close"].rolling(self.fast).mean()
        df["sma_slow"] = df["close"].rolling(self.slow).mean()
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        df["Signal"] = "HOLD"
        position = None
        entry_price = None

        for i in range(1, len(df)):
            prev_row = df.iloc[i - 1]
            curr_row = df.iloc[i]
            price = curr_row["close"]

            if position is None:
                if prev_row["sma_fast"] < prev_row["sma_slow"] and curr_row["sma_fast"] > curr_row["sma_slow"]:
                    df.at[i, "Signal"] = "BUY"
                    position = "LONG"
                    entry_price = price
                    log_trade(df.index[i], price, "BUY", position, entry_price)

            elif position == "LONG":
                if prev_row["sma_fast"] > prev_row["sma_slow"] and curr_row["sma_fast"] < curr_row["sma_slow"]:
                    df.at[i, "Signal"] = "SELL"
                    log_trade(df.index[i], price, "SELL", position, entry_price)
                    self.tracker.record_trade("WIN" if price > entry_price else "LOSS")
                    position = None
                    entry_price = None

        self.adapt_parameters()
        return df

    def generate_signal(self, df):
        df = self.generate_signals(df)
        return df["Signal"].iloc[-1]

    def adapt_parameters(self):
        summary = self.tracker.get_performance_summary()
        if summary["total_trades"] >= 5 and summary["win_rate"] < self.min_win_rate_threshold:
            logger.warning(f"?? Pausing {self.name} due to low win rate = {summary['win_rate']:.2f}")
            self.enabled = False

    def performance_summary(self):
        return self.tracker.get_performance_summary()
