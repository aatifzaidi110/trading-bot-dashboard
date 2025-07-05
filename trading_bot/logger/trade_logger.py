# logger/trade_logger.py

import os
import json
from datetime import datetime
import pandas as pd

LOG_FILE_JSON = "trades/trade_log.json"
LOG_FILE_CSV = "logs/trade_log.csv"

def safe_json_dump(data, path):
    import numpy as np

    def convert(o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, (np.bool_,)): return bool(o)
        if isinstance(o, (np.ndarray,)): return o.tolist()
        if isinstance(o, (datetime,)): return o.isoformat()
        return str(o)

    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=convert)

def log_trade(date, price, signal, position=None, entry_price=None, confidence=None, symbol=""):
    """
    Logs a trade entry with optional position, entry, and confidence.
    """
    trade = {
        "symbol": symbol,
        "Date": str(date),
        "Signal": signal,
        "entry": entry_price,
        "exit": price,
        "position": position,
        "confidence": confidence,
        "status": "PENDING"
    }

    os.makedirs(os.path.dirname(LOG_FILE_JSON), exist_ok=True)

    if os.path.exists(LOG_FILE_JSON):
        with open(LOG_FILE_JSON) as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                trades = []
    else:
        trades = []

    trades.append(trade)
    safe_json_dump(trades, LOG_FILE_JSON)

    # Also log to CSV for optional backup
    pct = None
    if position and entry_price:
        try:
            if position == "LONG":
                pct = round((price - entry_price) / entry_price * 100, 2)
            elif position == "SHORT":
                pct = round((entry_price - price) / entry_price * 100, 2)
        except ZeroDivisionError:
            pass

    row = {
        "timestamp": date,
        "symbol": symbol,
        "signal": signal,
        "position": position,
        "entry_price": entry_price,
        "exit_price": price,
        "confidence": confidence,
        "exit_profit_pct": pct
    }

    os.makedirs(os.path.dirname(LOG_FILE_CSV), exist_ok=True)
    if not os.path.exists(LOG_FILE_CSV):
        pd.DataFrame([row]).to_csv(LOG_FILE_CSV, index=False)
    else:
        pd.DataFrame([row]).to_csv(LOG_FILE_CSV, mode='a', header=False, index=False)

def save_vote_log(votes: list, filepath: str):
    if not votes:
        return
    df = pd.DataFrame(votes)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
