# tests/test_scan_logic.py

import pytest
from core.strategy.combo_strategy import ComboStrategy
from core.utils.data_loader import load_data

def test_combo_strategy_on_sample_ticker():
    symbol = "AAPL"
    df = load_data(symbol, period="1mo", interval="1d")
    assert df is not None and not df.empty, "Data should be loaded."

    strategy = ComboStrategy()
    result_df = strategy.generate_signals(df)

    assert not result_df.empty
    assert "Signal" in result_df.columns
    assert "Confidence" in result_df.columns

    # Check last signal value is valid
    last_row = result_df.iloc[-1]
    assert last_row["Signal"] in ["BUY", "HOLD", "TAKE_PROFIT", "STOP_LOSS"]
    assert 0 <= last_row["Confidence"] <= 5
