# tests/test_ticker_list.py

import os
import tempfile
from core.utils.ticker_list import get_top_tickers

def test_get_top_tickers_env(monkeypatch):
    monkeypatch.setenv("TICKER_LIST", "AAPL,GOOGL,MSFT")
    tickers = get_top_tickers()
    # Check all expected tickers are in the result
    for symbol in ["AAPL", "GOOGL", "MSFT"]:
        assert symbol in tickers

def test_get_top_tickers_file(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "top_tickers.txt")
        with open(config_path, "w") as f:
            f.write("TSLA\nNVDA\n")
        monkeypatch.setattr("core.utils.ticker_list.CONFIG_FILE", config_path)
        tickers = get_top_tickers()
        assert tickers == ["TSLA", "NVDA"]

def test_get_top_tickers_fallback():
    tickers = get_top_tickers()
    assert isinstance(tickers, list)
    assert "AAPL" in tickers
