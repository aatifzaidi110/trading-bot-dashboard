# tests/test_indicators.py

import pandas as pd
from core.indicators.indicators  import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_ema,
    calculate_sma
)

def test_all_indicators():
    data = pd.Series([i + 1 for i in range(100)])

    # RSI
    rsi = calculate_rsi(data, period=14)
    assert isinstance(rsi, pd.Series)
    assert len(rsi.dropna()) > 0

    # MACD
    macd, macd_signal = calculate_macd(data)
    assert isinstance(macd, pd.Series)
    assert isinstance(macd_signal, pd.Series)

    # Bollinger Bands
    ma, upper, lower = calculate_bollinger_bands(data)
    assert isinstance(ma, pd.Series)
    assert isinstance(upper, pd.Series)
    assert isinstance(lower, pd.Series)

    # EMA
    ema = calculate_ema(data)
    assert isinstance(ema, pd.Series)

    # SMA
    sma = calculate_sma(data)
    assert isinstance(sma, pd.Series)
