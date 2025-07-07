# scripts/download_data.py

import os
import sys
import yfinance as yf
import pandas as pd
from datetime import datetime

DEFAULT_SYMBOLS = ["AAPL", "MSFT", "TSLA", "SPY", "AMZN"]
DEFAULT_START = "2022-01-01"
DEFAULT_END = datetime.today().strftime("%Y-%m-%d")
DATA_DIR = "data"

def download_symbol(symbol, start, end):
    print(f"⬇️ Downloading: {symbol} | {start} → {end}")
    try:
        df = yf.download(symbol, start=start, end=end)
        if df.empty:
            print(f"⚠️ No data found for {symbol}")
            return
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index.name = "Date"
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(os.path.join(DATA_DIR, f"{symbol}.csv"))
        print(f"✅ Saved: {symbol}.csv")
    except Exception as e:
        print(f"❌ Failed for {symbol}: {e}")

if __name__ == "__main__":
    # CLI format: python download_data.py AAPL,MSFT,SPY 2022-01-01 2024-12-31
    symbols = sys.argv[1].split(",") if len(sys.argv) > 1 else DEFAULT_SYMBOLS
    start_date = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_START
    end_date = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_END

    for symbol in symbols:
        download_symbol(symbol.strip().upper(), start_date, end_date)
