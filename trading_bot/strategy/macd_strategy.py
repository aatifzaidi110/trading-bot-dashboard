# strategy/macd_strategy.py

import pandas as pd
import numpy as np
import logging
from utils.performance_tracker import PerformanceTracker
from logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class MACDStrategy:
    def __init__(self, fast=12, slow=26, signal=9, name="MACDStrategy"):
        self.fast = fast
        self.slow = slow
        self.signal = signal
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
        df["Signal"] = "HOLD"

        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["macd"] = df["ema_fast"] - df["ema_slow"]
        df["macd_signal"] = df["macd"].ewm(span=self.signal, adjust=False).mean()

        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        position = None
        entry_price = None

        for i in range(1, len(df)):
            prev_row = df.iloc[i - 1]
            row = df.iloc[i]
            price = row["close"]

            macd_cross_up = prev_row["macd"] < prev_row["macd_signal"] and row["macd"] > row["macd_signal"]
            macd_cross_down = prev_row["macd"] > prev_row["macd_signal"] and row["macd"] < row["macd_signal"]

            if position is None:
                if macd_cross_up:
                    df.at[i, "Signal"] = "BUY"
                    position = "LONG"
                    entry_price = price
                    log_trade(df.index[i], price, "BUY", "LONG", entry_price)

            elif position == "LONG":
                if macd_cross_down:
                    df.at[i, "Signal"] = "SELL"
                    log_trade(df.index[i], price, "SELL", "LONG", entry_price)
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
        if summary.get("total_trades", 0) >= 5 and summary.get("win_rate", 1.0) < self.min_win_rate_threshold:
            logger.warning(f"?? Pausing {self.name} due to low win rate = {summary['win_rate']:.2f}")
            self.enabled = False

    def performance_summary(self):
        return self.tracker.get_performance_summary()
