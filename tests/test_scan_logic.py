import pytest
from strategy.combo_strategy import ComboStrategy
from utils.data_loader import load_data

def test_combo_strategy_on_sample_ticker():
    symbol = "AAPL"
    df = load_data(symbol, period="1mo", interval="1d")
    assert df is not None and not df.empty, "Data should be loaded."

    strategy = ComboStrategy()
    result = strategy.evaluate(df)

    assert isinstance(result, dict)
    assert "signal" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 5
