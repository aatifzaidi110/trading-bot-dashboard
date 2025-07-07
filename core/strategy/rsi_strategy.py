# strategy/rsi_strategy.py

import pandas as pd
import logging
from core.utils.performance_tracker import PerformanceTracker
from core.logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class RSIStrategy:
    def __init__(self, period=14, oversold=30, overbought=70, name="RSIStrategy"):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.name = name
        self.tracker = PerformanceTracker(self.name)
        self.enabled = True
        self.min_win_rate_threshold = 0.3

    def calculate_rsi(self, series, period):
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signals(self, df):
        if not self.enabled:
            logger.info(f"🚫 Strategy {self.name} is paused.")
            df["Signal"] = "HOLD"
            return df

        df = df.copy()

        df["rsi"] = self.calculate_rsi(df["close"], self.period)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        if df.empty or "rsi" not in df.columns:
            logger.warning(f"⚠️ Not enough data to compute RSI for {self.name}")
            df["Signal"] = "HOLD"
            return df

        df["Signal"] = "HOLD"
        position = None
        entry_price = None

        for i in range(len(df)):
            row = df.iloc[i]
            price = row["close"]
            rsi = row["rsi"]

            if position is None and rsi < self.oversold:
                df.at[i, "Signal"] = "BUY"
                position = "LONG"
                entry_price = price
                log_trade(df.index[i], price, "BUY", "LONG", entry_price)

            elif position == "LONG" and rsi > self.overbought:
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
           logger.warning(f"⚠️ Pausing {self.name} due to low win rate = {summary['win_rate']:.2f}")
           self.enabled = False

    def performance_summary(self):
        return self.tracker.get_performance_summary()
