import pandas as pd

class ComboStrategy:
    def __init__(self, sma_window=50, rsi_period=14, rsi_buy=35, rsi_sell=65):
        self.sma_window = sma_window
        self.rsi_period = rsi_period
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df["SMA"] = df["close"].rolling(window=self.sma_window).mean()
        price = df["close"].iloc[-1]
        sma = df["SMA"].iloc[-1]

        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        rsi = df["RSI"].iloc[-1]

        if price > sma and rsi < self.rsi_buy:
            return "BUY"
        elif price < sma and rsi > self.rsi_sell:
            return "SELL"
        return "HOLD"
