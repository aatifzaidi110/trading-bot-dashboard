# trading_bot/indicators/indicators.py

import pandas as pd

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = -delta.clip(upper=0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal


def calculate_bollinger_bands(series: pd.Series, window: int = 20, std_dev: float = 2.0):
    ma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper = ma + std_dev * std
    lower = ma - std_dev * std
    return ma, upper, lower


def calculate_ema(series: pd.Series, span: int = 200):
    return series.ewm(span=span, adjust=False).mean()


def calculate_sma(series: pd.Series, window: int = 20):
    return series.rolling(window=window).mean()
