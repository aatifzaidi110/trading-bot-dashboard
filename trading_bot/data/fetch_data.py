import requests
import pandas as pd
from config import settings

def get_data(symbol, start_date, end_date, timeframe):
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/bars"
    headers = {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
    }
    params = {
        "start": start_date,
        "end": end_date,
        "timeframe": timeframe,
        "limit": 10000
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        bars = response.json().get("bars", [])
        if not bars:
            return None

        df = pd.DataFrame(bars)
        df['t'] = pd.to_datetime(df['t'])
        df.set_index('t', inplace=True)
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True)
        return df

    except Exception as e:
        print(f"Failed to fetch data for {symbol}: {e}")
        return None
