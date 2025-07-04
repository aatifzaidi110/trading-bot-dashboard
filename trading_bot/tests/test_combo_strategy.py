# tests/test_combo_strategy.py

import pandas as pd
from strategy.combo_strategy import ComboStrategy

def test_combo_strategy():
    # Sample dummy price data
    data = {
        "open": [100, 102, 104, 105, 107, 110, 108, 112, 115, 117, 119, 121, 120, 118, 116, 117, 119, 122, 125, 126, 128, 127],
        "high": [101, 103, 105, 106, 108, 111, 109, 113, 116, 118, 120, 122, 121, 119, 117, 118, 120, 123, 126, 127, 129, 128],
        "low":  [99, 100, 102, 103, 106, 108, 107, 110, 114, 115, 117, 119, 118, 116, 114, 115, 117, 120, 123, 124, 126, 125],
        "close": [100, 101, 103, 104, 107, 109, 108, 111, 115, 117, 118, 120, 119, 117, 115, 116, 118, 121, 124, 125, 127, 126],
        "volume": [100000]*22
    }

    df = pd.DataFrame(data)
    df.index = pd.date_range(start="2023-01-01", periods=len(df))

    strat = ComboStrategy()
    df_signals = strat.generate_signals(df)
    signal = strat.generate_signal(df)

    print("✅ Latest Signal:", signal)
    print(df_signals.tail(3)[["close", "Signal"]])

if __name__ == "__main__":
    test_combo_strategy()
