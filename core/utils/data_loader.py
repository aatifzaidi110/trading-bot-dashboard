# utils/data_loader.py

import os
import pandas as pd
import yfinance as yf

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def load_data(symbol, period="1y", interval="1d"):
    """
    Load price data for a single ticker from disk or yfinance.
    """
    file_path = os.path.join(DATA_DIR, f"{symbol}.csv")

    # Try loading from disk
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, parse_dates=["Date"])
            df.set_index("Date", inplace=True)
            df.columns = df.columns.str.lower()
            if "close" not in df.columns:
                print(f"⚠️ Skipping {symbol}: 'close' column missing in local file.")
                return None
            return df
        except Exception as e:
            print(f"⚠️ Error reading local file for {symbol}: {e}")

    # Fallback to yfinance
    try:
        df = yf.download(symbol, period=period, interval=interval)
        if df.empty:
            print(f"⚠️ No data for {symbol} from Yahoo.")
            return None

        df.reset_index(inplace=True)

        # Flatten multi-index if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.columns = df.columns.str.lower()
        if "date" in df.columns:
            df.rename(columns={"date": "Date"}, inplace=True)

        if "close" not in df.columns:
            print(f"⚠️ Skipping {symbol}: 'close' column missing from Yahoo.")
            return None

        # Save locally
        df.to_csv(file_path, index=False)
        df.set_index("Date", inplace=True)
        return df

    except Exception as e:
        print(f"⚠️ Failed to load {symbol} from yfinance: {e}")
        return None


# ✅ Alias to fix broken imports
def load_price_data(symbol, period="1y", interval="1d"):
    return load_data(symbol, period, interval)


def load_csv(filepath):
    """
    Load a CSV file manually from path (used in dashboards, uploads, etc.)
    """
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df


def load_all_price_data(tickers: list, period="1y", interval="1d") -> dict:
    """
    Load price data for a list of tickers.
    Returns a dictionary: { 'AAPL': df, 'TSLA': df, ... }
    """
    data = {}
    for symbol in tickers:
        df = load_data(symbol, period, interval)
        if df is not None:
            data[symbol] = df
    return data
