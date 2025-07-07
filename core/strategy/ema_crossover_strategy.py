# strategy/ema_crossover_strategy.py

import pandas as pd
import logging
from logger.trade_logger import log_trade
from utils.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)

class EMACrossoverStrategy:
    def __init__(self, short_period=20, long_period=50, stop_loss_pct=0.02, take_profit_pct=0.04, name="EMACrossoverStrategy"):
        self.name = name
        self.short_period = short_period
        self.long_period = long_period
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.tracker = PerformanceTracker(self.name)
        self.enabled = True
        self.min_win_rate_threshold = 0.3

    def generate_signals(self, df):
        if not self.enabled:
            logger.info(f"🚫 Strategy {self.name} is paused.")
            df["Signal"] = "HOLD"
            return df

        df = df.copy()
        df["ema_short"] = df["close"].ewm(span=self.short_period, adjust=False).mean()
        df["ema_long"] = df["close"].ewm(span=self.long_period, adjust=False).mean()
        df["Signal"] = "HOLD"

        position = None
        entry_price = None

        for i in range(self.long_period, len(df)):
            short_ema = df["ema_short"].iloc[i]
            long_ema = df["ema_long"].iloc[i]
            price = df["close"].iloc[i]

            if position is None:
                if short_ema > long_ema:
                    df.at[df.index[i], "Signal"] = "BUY"
                    position = "LONG"
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
            # Make the strategy more aggressive
            self.short_period = max(5, self.short_period - 2)
            self.long_period = max(10, self.long_period - 5)
            logger.info(f"🔁 Adjusted EMA periods: short={self.short_period}, long={self.long_period}")

    def performance_summary(self):
        return self.tracker.get_performance_summary()