# tests/test_stats_parser.py

import pytest
from datetime import datetime
from trading_bot.utils.performance_tracker import PerformanceTracker

def test_performance_summary():
    tracker = PerformanceTracker("TestStrategy")
    
    tracker.record_trade("WIN", pnl=2.5)
    tracker.record_trade("LOSS", pnl=-1.0)
    tracker.record_trade("WIN", pnl=3.0)

    summary = tracker.get_performance_summary()
    
    assert summary["total_trades"] == 3
    assert summary["wins"] == 2
    assert summary["losses"] == 1
    assert round(summary["win_rate"], 2) == 0.67
    assert summary["Return (%)"] == pytest.approx(4.5)
