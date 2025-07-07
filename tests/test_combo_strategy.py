# tests/test_combo_strategy.py

import pandas as pd
import pytest
from trading_bot.strategy.combo_strategy import ComboStrategy


@pytest.fixture
def sample_price_data():
    """
    Creates a dummy price DataFrame with enough rows for indicators to work.
    """
    dates = pd.date_range(end=pd.Timestamp.today(), periods=100)
    prices = [100 + i * 0.5 for i in range(100)]
    df = pd.DataFrame({
        "Date": dates,
        "close": prices
    })
    return df

def test_generate_signals_structure(sample_price_data):
    strategy = ComboStrategy()
    result_df = strategy.generate_signals(sample_price_data)
    
    assert isinstance(result_df, pd.DataFrame)
    assert "Signal" in result_df.columns
    assert "Reason" in result_df.columns
    assert "Confidence" in result_df.columns
    assert len(result_df) > 0

def test_generate_signal_value(sample_price_data):
    strategy = ComboStrategy()
    signal = strategy.generate_signal(sample_price_data)
    
    assert signal in ["BUY", "HOLD", "STOP_LOSS", "TAKE_PROFIT"]

def test_adapt_parameters_safely():
    strategy = ComboStrategy()
    # Force strategy to adapt with dummy bad performance
    strategy.tracker.trades = [{"result": "LOSS"}] * 15
    strategy.adapt_parameters()
    
    assert strategy.enabled is False or isinstance(strategy.rsi_threshold, int)

def test_strategy_generates_signals():
    data = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=100),
        "close": [100 + i for i in range(100)]
    })
    strategy = ComboStrategy()
    signals = strategy.generate_signals(data)
    assert not signals.empty