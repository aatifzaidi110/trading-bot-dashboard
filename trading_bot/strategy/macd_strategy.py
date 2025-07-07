import pandas as pd

class MACDStrategy:
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df["EMA_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["EMA_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["MACD"] = df["EMA_fast"] - df["EMA_slow"]
        df["Signal_Line"] = df["MACD"].ewm(span=self.signal, adjust=False).mean()

        if df["MACD"].iloc[-2] < df["Signal_Line"].iloc[-2] and df["MACD"].iloc[-1] > df["Signal_Line"].iloc[-1]:
            return "BUY"
        elif df["MACD"].iloc[-2] > df["Signal_Line"].iloc[-2] and df["MACD"].iloc[-1] < df["Signal_Line"].iloc[-1]:
            return "SELL"
        return "HOLD"
