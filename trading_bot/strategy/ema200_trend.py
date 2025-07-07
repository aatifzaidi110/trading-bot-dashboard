import pandas as pd

class EMA200Strategy:
    def __init__(self):
        pass

    def generate_signal(self, df: pd.DataFrame):
        df = df.copy()
        df["EMA200"] = df["close"].ewm(span=200, adjust=False).mean()
        price = df["close"].iloc[-1]
        ema = df["EMA200"].iloc[-1]

        if price > ema:
            return "BUY"
        elif price < ema:
            return "SELL"
        return "HOLD"
