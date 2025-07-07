from strategy.rsi_strategy import RSIStrategy
from strategy.sma_crossover import SMACrossoverStrategy
from strategy.macd_strategy import MACDStrategy

class EnsembleStrategy:
    def __init__(self):
        self.strategies = [
            RSIStrategy(14, 30, 70),
            SMACrossoverStrategy(20, 50),
            MACDStrategy()
        ]

    def generate_signal(self, df):
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for strat in self.strategies:
            signal = strat.generate_signal(df)
            votes[signal] += 1

        if votes["BUY"] >= 2:
            return "BUY"
        elif votes["SELL"] >= 2:
            return "SELL"
        else:
            return "HOLD"
