# logger/trade_logger.py

import os
import pandas as pd
from datetime import datetime

LOG_FILE = "logs/trade_log.csv"

def log_trade(timestamp, price, signal, position=None, entry_price=None):
    """
    Logs trade information including profit percentage if position and entry_price are provided.
    """

    # Calculate profit % if possible
    if position is not None and entry_price is not None:
        try:
            if position == "LONG":
                pct = round((price - entry_price) / entry_price * 100, 2)
            elif position == "SHORT":
                pct = round((entry_price - price) / entry_price * 100, 2)
            else:
                pct = None
        except ZeroDivisionError:
            pct = None
    else:
        pct = None

    # Format row
    row = {
        "timestamp": timestamp,
        "price": price,
        "signal": signal,
        "position": position,
        "entry_price": entry_price,
        "exit_profit_pct": pct
    }

    # Save to CSV
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        pd.DataFrame([row]).to_csv(LOG_FILE, index=False)
    else:
        pd.DataFrame([row]).to_csv(LOG_FILE, mode='a', header=False, index=False)

def save_vote_log(votes: list, filepath: str):
    """
    Save the voting breakdown (BUY/SELL/HOLD from each strategy) to a CSV file.
    """
    import pandas as pd
    import os

    if not votes:
        return

    df = pd.DataFrame(votes)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
