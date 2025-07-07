# data/fetch_yahoo_data.py

import yfinance as yf

def fetch_yahoo_data(symbol, start="2022-01-01", end="2025-06-01"):
    df = yf.download(symbol, start=start, end=end)
    df = df.rename(columns=str.lower)
    df = df[["open", "high", "low", "close", "volume"]]
    df.dropna(inplace=True)
    return df
