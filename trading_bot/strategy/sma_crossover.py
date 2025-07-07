import pandas as pd

class SMACrossoverStrategy:
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df['SMA_Short'] = df['close'].rolling(window=self.short_window).mean()
        df['SMA_Long'] = df['close'].rolling(window=self.long_window).mean()

        if df['SMA_Short'].iloc[-2] < df['SMA_Long'].iloc[-2] and df['SMA_Short'].iloc[-1] > df['SMA_Long'].iloc[-1]:
            return "BUY"
        elif df['SMA_Short'].iloc[-2] > df['SMA_Long'].iloc[-2] and df['SMA_Short'].iloc[-1] < df['SMA_Long'].iloc[-1]:
            return "SELL"
        return "HOLD"
