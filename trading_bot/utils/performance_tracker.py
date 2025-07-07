# utils/performance_tracker.py

__all__ = ["PerformanceTracker", "save_performance_summary"]

class PerformanceTracker:
    """
    Tracks trade outcomes and performance stats.
    Used to dynamically adjust strategy logic based on results.
    """
    def __init__(self, strategy_name=""):
        self.strategy_name = strategy_name
        self.reset()

    def reset(self):
        self.wins = 0
        self.losses = 0
        self.total_return = 0
        self.trade_history = []

    def record_trade(self, result, pnl=0):
        result = result.upper()
        if result == "WIN":
            self.wins += 1
        elif result == "LOSS":
            self.losses += 1

        self.total_return += pnl
        self.trade_history.append(result)

    def get_performance_summary(self):
        total_trades = self.wins + self.losses
        win_rate = self.wins / total_trades if total_trades else 0

        return {
            "strategy": self.strategy_name,
            "total_trades": total_trades,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": round(win_rate, 2),
            "Return (%)": round(self.total_return, 2)
        }

def save_performance_summary(summary, path):
    import json, os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
