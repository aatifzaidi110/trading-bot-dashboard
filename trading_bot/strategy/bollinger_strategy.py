import pandas as pd

class BollingerStrategy:
    def __init__(self, window=20, num_std=2):
        self.window = window
        self.num_std = num_std

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        rolling_mean = df["close"].rolling(self.window).mean()
        rolling_std = df["close"].rolling(self.window).std()
        df["Upper"] = rolling_mean + (self.num_std * rolling_std)
        df["Lower"] = rolling_mean - (self.num_std * rolling_std)

        price = df["close"].iloc[-1]
        if price < df["Lower"].iloc[-1]:
            return "BUY"
        elif price > df["Upper"].iloc[-1]:
            return "SELL"
        return "HOLD"
