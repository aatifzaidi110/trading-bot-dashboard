# data/fetch_data.py

import yfinance as yf
import pandas as pd

def get_data(symbol, start_date, end_date, timeframe="1d"):
    try:
        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=timeframe,
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            print(f"⚠️ No data for {symbol}")
            return None

        # Flatten multi-index columns if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]

        expected_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ {symbol} missing expected columns: {missing_cols}")
            return None

        df = df[expected_cols]
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)

        return df

    except Exception as e:
        print(f"❌ Failed to fetch data for {symbol}: {e}")
        return None