import pandas as pd

class RSIStrategy:
    def __init__(self, period=14, lower=30, upper=70):
        self.period = period
        self.lower = lower
        self.upper = upper

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        if df["RSI"].iloc[-1] < self.lower:
            return "BUY"
        elif df["RSI"].iloc[-1] > self.upper:
            return "SELL"
        return "HOLD"
