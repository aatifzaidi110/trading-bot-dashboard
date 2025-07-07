# strategy/ma_crossover_strategy.py

import pandas as pd
import logging
from utils.performance_tracker import PerformanceTracker
from logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class MACrossoverStrategy:
    def __init__(
        self,
        short_window=20,
        long_window=50,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        name="MACrossoverStrategy"
    ):
        self.short_window = short_window
        self.long_window = long_window
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
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
        df["short_ma"] = df["close"].rolling(window=self.short_window).mean()
        df["long_ma"] = df["close"].rolling(window=self.long_window).mean()
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df["Signal"] = "HOLD"

        position = None
        entry_price = None

        for i in range(1, len(df)):
            prev = df.iloc[i - 1]
            curr = df.iloc[i]
            price = curr["close"]

            # Buy signal
            if position is None and prev["short_ma"] <= prev["long_ma"] and curr["short_ma"] > curr["long_ma"]:
                df.at[i, "Signal"] = "BUY"
                position = "LONG"
                entry_price = price
                log_trade(df.index[i], price, "BUY", "LONG", entry_price)

            elif position == "LONG":
                stop_loss = entry_price * (1 - self.stop_loss_pct)
                take_profit = entry_price * (1 + self.take_profit_pct)

                if price <= stop_loss:
                    df.at[i, "Signal"] = "STOP_LOSS"
                    log_trade(df.index[i], price, "STOP_LOSS", "LONG", entry_price)
                    self.tracker.record_trade("LOSS")
                    position = None
                    entry_price = None

                elif price >= take_profit:
                    df.at[i, "Signal"] = "TAKE_PROFIT"
                    log_trade(df.index[i], price, "TAKE_PROFIT", "LONG", entry_price)
                    self.tracker.record_trade("WIN")
                    position = None
                    entry_price = None

        self.adapt_behavior()
        return df

    def generate_signal(self, df):
        df = self.generate_signals(df)
        if df.empty or "Signal" not in df.columns:
            return "HOLD"
        return df["Signal"].iloc[-1]

    def adapt_behavior(self):
        summary = self.tracker.get_performance_summary()
        if summary["total_trades"] >= 5 and summary["win_rate"] < self.min_win_rate_threshold:
           logger.warning(f"⚠️ Pausing {self.name} due to low win rate = {summary['win_rate']:.2f}")
           self.enabled = False


    def performance_summary(self):
        return self.tracker.get_performance_summary()
