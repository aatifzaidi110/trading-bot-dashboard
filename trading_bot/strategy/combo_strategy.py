import pandas as pd
import numpy as np
import logging
from utils.performance_tracker import PerformanceTracker
from logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class ComboStrategy:
    def __init__(
        self,
        sma_fast=20,
        sma_slow=50,
        rsi_period=14,
        rsi_threshold=30,
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        bollinger_window=20,
        bollinger_std=2,
        ema_period=200,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        name="ComboStrategy"
    ):
        self.sma_fast = sma_fast
        self.sma_slow = sma_slow
        self.rsi_period = rsi_period
        self.rsi_threshold = rsi_threshold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bollinger_window = bollinger_window
        self.bollinger_std = bollinger_std
        self.ema_period = ema_period
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.name = name
        self.tracker = PerformanceTracker(self.name)
        self.enabled = True
        self.min_win_rate_threshold = 0.1  # lowered threshold
        self.vote_log = []

    def calculate_rsi(self, series, period):
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signals(self, df):
        if df is None or len(df) == 0:
            return pd.DataFrame()

        if not self.enabled:
            logger.info(f"🚫 Strategy {self.name} is paused.")
            df["Signal"] = "HOLD"
            return df

        df = df.copy()
        df["Signal"] = "HOLD"
        df["Reason"] = ""
        df["Confidence"] = 0

        df["sma_fast"] = df["close"].rolling(self.sma_fast).mean()
        df["sma_slow"] = df["close"].rolling(self.sma_slow).mean()
        df["rsi"] = self.calculate_rsi(df["close"], self.rsi_period)
        df["ema200"] = df["close"].ewm(span=self.ema_period).mean()

        exp1 = df["close"].ewm(span=self.macd_fast, adjust=False).mean()
        exp2 = df["close"].ewm(span=self.macd_slow, adjust=False).mean()
        df["macd"] = exp1 - exp2
        df["macd_signal"] = df["macd"].ewm(span=self.macd_signal, adjust=False).mean()

        df["ma"] = df["close"].rolling(window=self.bollinger_window).mean()
        df["std"] = df["close"].rolling(window=self.bollinger_window).std()
        df["upper"] = df["ma"] + self.bollinger_std * df["std"]
        df["lower"] = df["ma"] - self.bollinger_std * df["std"]

        df.dropna(inplace=True)
        df.reset_index(drop=False, inplace=True)

        position = None
        entry_price = None

        min_index = max(
            self.sma_slow,
            self.bollinger_window,
            self.ema_period,
            self.rsi_period,
            self.macd_slow + self.macd_signal
        )

        for i in range(min_index, len(df)):
            row = df.iloc[i]
            price = row["close"]

            # === Indicator checks ===
            trend_up = price > row["ema200"]
            rsi_signal = row["rsi"] < self.rsi_threshold
            macd_cross = row["macd"] > row["macd_signal"]
            bollinger_touch = price < row["lower"]
            crossover = row["sma_fast"] > row["sma_slow"]

            indicators_passed = {
                "trend_up": trend_up,
                "rsi_signal": rsi_signal,
                "macd_cross": macd_cross,
                "bollinger_touch": bollinger_touch,
                "sma_crossover": crossover,
            }

            confidence = sum(indicators_passed.values())

            reasons = [f"{k}={'✅' if v else '❌'}" for k, v in indicators_passed.items()]
            signal = "HOLD"

            if position is None:
                if confidence == 5:
                    signal = "BUY"
                    position = "LONG"
                    entry_price = price
                    log_trade(df.at[i, "Date"], price, signal, "LONG", entry_price)

            elif position == "LONG":
                stop_loss = entry_price * (1 - self.stop_loss_pct)
                take_profit = entry_price * (1 + self.take_profit_pct)

                if price <= stop_loss:
                    signal = "STOP_LOSS"
                    self.tracker.record_trade("LOSS")
                    log_trade(df.at[i, "Date"], price, signal, "LONG", entry_price)
                    position = None
                    entry_price = None

                elif price >= take_profit:
                    signal = "TAKE_PROFIT"
                    self.tracker.record_trade("WIN")
                    log_trade(df.at[i, "Date"], price, signal, "LONG", entry_price)
                    position = None
                    entry_price = None

            df.at[i, "Signal"] = signal
            df.at[i, "Reason"] = "; ".join(reasons)
            df.at[i, "Confidence"] = confidence

            self.vote_log.append({
                "Date": df.at[i, "Date"],
                "Price": price,
                "Signal": signal,
                "Confidence": confidence,
                **indicators_passed
            })

        self.adapt_parameters()
        return df

    def generate_signal(self, df):
        df = self.generate_signals(df)
        return df["Signal"].iloc[-1]

    def adapt_parameters(self):
        summary = self.tracker.get_performance_summary()

        if summary.get("total_trades", 0) < 10:
            return  # not enough data to judge performance yet

        if summary.get("win_rate", 1) < self.min_win_rate_threshold:
            logger.warning(f"⚠️ Pausing {self.name} due to low win rate = {summary['win_rate']:.2f}")
            self.enabled = False
        elif summary.get("win_rate", 0) > 0.6:
            self.rsi_threshold = max(10, self.rsi_threshold - 2)
            self.bollinger_std = max(1.5, self.bollinger_std - 0.1)
            logger.info(f"🔁 Adjusted parameters: rsi={self.rsi_threshold}, boll_std={self.bollinger_std:.2f}")

    def get_performance_summary(self):
        return self.tracker.get_performance_summary()
