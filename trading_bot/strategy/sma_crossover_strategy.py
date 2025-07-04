# strategy/sma_crossover_strategy.py

import pandas as pd
import logging
from utils.performance_tracker import PerformanceTracker
from logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class SMACrossoverStrategy:
    def __init__(
        self,
        sma_fast=20,
        sma_slow=50,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        name="SMACrossoverStrategy"
    ):
        self.sma_fast = sma_fast
        self.sma_slow = sma_slow
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.name = name
        self.tracker = PerformanceTracker(name)
        self.enabled = True
        self.min_win_rate_threshold = 0.3

    def generate_signals(self, df):
        if not self.enabled:
            logger.info(f"🚫 Strategy {self.name} is paused.")
            df["Signal"] = "HOLD"
            return df

        df = df.copy()
        df["sma_fast"] = df["close"].rolling(window=self.sma_fast).mean()
        df["sma_slow"] = df["close"].rolling(window=self.sma_slow).mean()
        df["Signal"] = "HOLD"

        position = None
        entry_price = None

        for i in range(self.sma_slow, len(df)):
            prev_fast = df["sma_fast"].iloc[i - 1]
            prev_slow = df["sma_slow"].iloc[i - 1]
            curr_fast = df["sma_fast"].iloc[i]
            curr_slow = df["sma_slow"].iloc[i]
            price = df["close"].iloc[i]

            if position is None:
                if prev_fast < prev_slow and curr_fast > curr_slow:
                    df.at[df.index[i], "Signal"] = "BUY"
                    position = "LONG"
                    entry_price = price
                elif prev_fast > prev_slow and curr_fast < curr_slow:
                    df.at[df.index[i], "Signal"] = "SELL"
                    position = "SHORT"
                    entry_price = price

            elif position == "LONG":
                stop_loss = entry_price * (1 - self.stop_loss_pct)
                take_profit = entry_price * (1 + self.take_profit_pct)

                if price <= stop_loss:
                    df.at[df.index[i], "Signal"] = "STOP_LOSS"
                    log_trade(df.index[i], price, "STOP_LOSS", "LONG", entry_price)
                    self.tracker.record_trade("LOSS")
                    position = None
                    entry_price = None
                elif price >= take_profit:
                    df.at[df.index[i], "Signal"] = "TAKE_PROFIT"
                    log_trade(df.index[i], price, "TAKE_PROFIT", "LONG", entry_price)
                    self.tracker.record_trade("WIN")
                    position = None
                    entry_price = None

            elif position == "SHORT":
                stop_loss = entry_price * (1 + self.stop_loss_pct)
                take_profit = entry_price * (1 - self.take_profit_pct)

                if price >= stop_loss:
                    df.at[df.index[i], "Signal"] = "STOP_LOSS"
                    log_trade(df.index[i], price, "STOP_LOSS", "SHORT", entry_price)
                    self.tracker.record_trade("LOSS")
                    position = None
                    entry_price = None
                elif price <= take_profit:
                    df.at[df.index[i], "Signal"] = "TAKE_PROFIT"
                    log_trade(df.index[i], price, "TAKE_PROFIT", "SHORT", entry_price)
                    self.tracker.record_trade("WIN")
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
           logger.warning(f"⚠️ Pausing {self.name} due to low win rate = {summary['win_rate']:.2f}")
           self.enabled = False
        elif summary["win_rate"] > 0.6 and summary["total_trades"] >= 20:
            self.sma_fast = max(5, self.sma_fast - 1)
            self.sma_slow = max(self.sma_fast + 10, self.sma_slow - 2)
            logger.info(f"🔁 Tuned SMAs: fast={self.sma_fast}, slow={self.sma_slow}")

    def performance_summary(self):
        return self.tracker.get_performance_summary()