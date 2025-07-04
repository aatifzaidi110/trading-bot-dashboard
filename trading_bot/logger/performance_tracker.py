# logger/performance_tracker.py
import json
import os
import csv
from datetime import datetime

LOG_DIR = "logs/performance"
os.makedirs(LOG_DIR, exist_ok=True)

CSV_FILE = os.path.join(LOG_DIR, "strategy_performance_log.csv")


def load_performance_summary(file_path):
    try:
        with open(file_path) as f:
            return json.load(f)
    except Exception:
        return {
            "Return (%)": 0,
            "Sharpe Ratio": 0,
            "Max Drawdown (%)": 0,
            "total_trades": 0,
            "win_rate": 0
        }
        
def save_performance_summary(summary: dict, filepath: str):
    """
    Save performance metrics (like returns, sharpe ratio, final value) as a JSON file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(summary, f, indent=4)

def log_result(symbol, result: dict, strategy_name: str):
    """
    Logs performance metrics for each backtest run to CSV.
    """
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "Timestamp", "Symbol", "Strategy", "Start", "End",
            "Final Value", "Return (%)", "Sharpe Ratio", "Max Drawdown (%)"
        ])
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "Timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "Symbol": symbol,
            "Strategy": strategy_name,
            "Start": result.get("Start"),
            "End": result.get("End"),
            "Final Value": float(result.get("Final Value", 0)),
            "Return (%)": float(result.get("Return (%)", 0)),
            "Sharpe Ratio": float(result.get("Sharpe Ratio", 0)),
            "Max Drawdown (%)": float(result.get("Max Drawdown (%)", 0))
        })