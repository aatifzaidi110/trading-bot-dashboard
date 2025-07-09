# core/utils/cleaning.py

import pandas as pd

def clean_ml_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare ML prediction + close price chart data.
    """
    df = df.copy()
    required_cols = ["Date", "ml_prediction", "close"]

    if not all(col in df.columns for col in required_cols):
        return pd.DataFrame()

    df = df[required_cols]
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df["ml_prediction"] = pd.to_numeric(df["ml_prediction"], errors='coerce')
    df["close"] = pd.to_numeric(df["close"], errors='coerce')
    df.dropna(inplace=True)

    return df
