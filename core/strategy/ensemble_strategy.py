import logging
from core.strategy.rsi_strategy import RSIStrategy
from core.strategy.macd_strategy import MACDStrategy
from core.strategy.ema200_trend import EMA200TrendStrategy
from core.strategy.bollinger_strategy import BollingerStrategy
from core.strategy.combo_strategy import ComboStrategy
from core.strategy.sma_crossover_strategy import SMACrossoverStrategy
from core.utils.performance_tracker import PerformanceTracker
from core.logger.trade_logger import log_trade

logger = logging.getLogger(__name__)

class EnsembleStrategy:
    def __init__(self, name="EnsembleStrategy"):
        self.name = name
        self.voters = [
            RSIStrategy(),
            MACDStrategy(),
            EMA200TrendStrategy(),
            BollingerStrategy(),
            ComboStrategy(),
            SMACrossoverStrategy()
        ]
        self.tracker = PerformanceTracker(name)

    def generate_signals(self, df):
        df = df.copy()
        df["Signal"] = "HOLD"
        votes = []

        for voter in self.voters:
            try:
                signal = voter.generate_signal(df)
                votes.append(signal)
            except Exception as e:
                logger.warning(f"⚠️ {voter.name} failed: {str(e)}")
                votes.append("HOLD")

        vote_count = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for vote in votes:
            vote_count[vote] += 1

        logger.info(f"🧠 Ensemble votes: {vote_count} => Final: {max(vote_count, key=vote_count.get)}")
        final_signal = max(vote_count, key=vote_count.get)
        df.at[df.index[-1], "Signal"] = final_signal

        # Log trade if actionable
        if final_signal in ["BUY", "SELL"]:
            log_trade(df.index[-1], df["close"].iloc[-1], final_signal, "ENSEMBLE", df["close"].iloc[-1])

        return df, votes

    def generate_signal(self, df):
        df, _ = self.generate_signals(df)
        return df["Signal"].iloc[-1]

    def performance_summary(self):
        return self.tracker.get_performance_summary()
