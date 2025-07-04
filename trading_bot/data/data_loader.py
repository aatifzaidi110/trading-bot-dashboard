import pandas as pd
import os

def load_data(symbol, folder="data", file_ext=".csv"):
    path = os.path.join(folder, f"{symbol.upper()}{file_ext}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Data file not found: {path}")
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    df.sort_index(inplace=True)
    return df