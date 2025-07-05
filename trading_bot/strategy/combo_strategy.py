# strategy/combo_strategy.py

import pandas as pd
import logging
from trading_bot.utils.performance_tracker import PerformanceTracker
from trading_bot.logger.trade_logger import log_trade
from indicators.indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_ema,
    calculate_sma
)

logger = logging.getLogger(__name__)

class ComboStrategy:
    def __init__(self, sma_fast=20, sma_slow=50, rsi_period=14, rsi_threshold=30,
                 macd_fast=12, macd_slow=26, macd_signal=9,
                 bollinger_window=20, bollinger_std=2, ema_period=200,
                 stop_loss_pct=0.02, take_profit_pct=0.04, name="ComboStrategy"):
        self.name = name
        self.enabled = True
        self.min_win_rate_threshold = 0.1
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
        self.tracker = PerformanceTracker(self.name)
        self.vote_log = []

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            logger.warning("📉 Empty data passed to strategy.")
            return pd.DataFrame()

        if not self.enabled:
            logger.info(f"🚫 Strategy {self.name} is paused.")
            df["Signal"] = "HOLD"
            return df

        df = df.copy()
        df["Signal"] = "HOLD"
        df["Reason"] = ""
        df["Confidence"] = 0

        # === Indicators ===
        df["sma_fast"] = calculate_sma(df["close"], self.sma_fast)
        df["sma_slow"] = calculate_sma(df["close"], self.sma_slow)
        df["rsi"] = calculate_rsi(df["close"], self.rsi_period)
        df["ema200"] = calculate_ema(df["close"], self.ema_period)
        df["macd"], df["macd_signal"] = calculate_macd(df["close"], self.macd_fast, self.macd_slow, self.macd_signal)
        df["ma"], df["upper"], df["lower"] = calculate_bollinger_bands(df["close"], self.bollinger_window, self.bollinger_std)

        df.dropna(inplace=True)
        df.reset_index(drop=False, inplace=True)

        position = None
        entry_price = None

        for i in range(len(df)):
            row = df.iloc[i]
            price = row["close"]

            indicators = {
                "trend_up": price > row["ema200"],
                "rsi_signal": row["rsi"] < self.rsi_threshold,
                "macd_cross": row["macd"] > row["macd_signal"],
                "bollinger_touch": price < row["lower"],
                "sma_crossover": row["sma_fast"] > row["sma_slow"],
            }

            confidence = sum(indicators.values())
            reasons = [f"{k}={'✅' if v else '❌'}" for k, v in indicators.items()]
            signal = "HOLD"

            # === Buy Logic ===
            if position is None and confidence == 5:
                signal = "BUY"
                position = "LONG"
                entry_price = price
                log_trade(row["Date"], price, signal, position, entry_price)

            # === Exit Logic ===
            elif position == "LONG":
                stop_loss = entry_price * (1 - self.stop_loss_pct)
                take_profit = entry_price * (1 + self.take_profit_pct)

                if price <= stop_loss:
                    signal = "STOP_LOSS"
                    pct = round((price - entry_price) / entry_price * 100, 2)
                    self.tracker.record_trade("LOSS", pnl=pct)
                    log_trade(row["Date"], price, signal, position, entry_price)
                    position = None
                    entry_price = None

                elif price >= take_profit:
                    signal = "TAKE_PROFIT"
                    pct = round((price - entry_price) / entry_price * 100, 2)
                    self.tracker.record_trade("WIN", pnl=pct)
                    log_trade(row["Date"], price, signal, position, entry_price)
                    position = None
                    entry_price = None

            df.at[i, "Signal"] = signal
            df.at[i, "Reason"] = "; ".join(reasons)
            df.at[i, "Confidence"] = confidence

            self.vote_log.append({
                "Date": row["Date"],
                "Price": price,
                "Signal": signal,
                "Confidence": confidence,
                **indicators
            })

        self.adapt_parameters()
        return df

    def generate_signal(self, df: pd.DataFrame) -> str:
        df_signals = self.generate_signals(df)
        return df_signals["Signal"].iloc[-1] if not df_signals.empty else "HOLD"

    def adapt_parameters(self):
        summary = self.tracker.get_performance_summary()
        if summary.get("total_trades", 0) < 10:
            return

        win_rate = summary.get("win_rate", 1)
        if win_rate < self.min_win_rate_threshold:
            logger.warning(f"⚠️ Pausing {self.name} due to low win rate = {win_rate:.2f}")
            self.enabled = False
        elif win_rate > 0.6:
            self.rsi_threshold = max(10, self.rsi_threshold - 2)
            self.bollinger_std = max(1.5, self.bollinger_std - 0.1)
            logger.info(f"🔁 Adjusted parameters: rsi={self.rsi_threshold}, boll_std={self.bollinger_std:.2f}")

    def get_performance_summary(self):
        return self.tracker.get_performance_summary()
        
        def adapt_parameters(self):
        """
        Automatically adjust confidence requirements based on win rate.
        """
        summary = self.tracker.get_performance_summary()
        total = summary.get("total_trades", 0)
        win_rate = summary.get("win_rate", 1)

        if total < 10:
            return  # Not enough data yet

        # Tune threshold
        if win_rate < 0.4:
            self.rsi_threshold += 2
            self.bollinger_std += 0.2
            self.min_win_rate_threshold = min(0.5, self.min_win_rate_threshold + 0.05)
            logger.warning(f"📉 Strategy underperforming. Raised RSI threshold and Bollinger STD.")

        elif win_rate > 0.6:
            self.rsi_threshold = max(10, self.rsi_threshold - 2)
            self.bollinger_std = max(1.5, self.bollinger_std - 0.1)
            self.min_win_rate_threshold = max(0.1, self.min_win_rate_threshold - 0.05)
            logger.info(f"📈 Strategy improving. Loosened RSI and Bollinger for more entries.")

