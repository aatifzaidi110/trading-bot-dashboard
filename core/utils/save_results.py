# utils/save_results.py

import os
import pandas as pd
import json

def save_strategy_results(symbol, strategy_name, df, votes=None, summary=None, folder="results"):
    """
    Save strategy output (signals, votes, performance summary) for dashboards and reporting.
    """

    symbol = symbol.upper()
    path = os.path.join(folder, strategy_name.lower())
    os.makedirs(path, exist_ok=True)

    # ✅ Save signal + indicators
    df_path = os.path.join(path, f"{symbol}_signals.csv")
    df.to_csv(df_path)

    # ✅ Save voting breakdown (if provided)
    if votes:
        if isinstance(votes, list):
            votes_df = pd.DataFrame(votes)
        elif isinstance(votes, dict):
            votes_df = pd.DataFrame([votes])
        else:
            raise ValueError("Votes must be dict or list of dicts")

        votes_path = os.path.join(path, f"{symbol}_votes.csv")
        votes_df.to_csv(votes_path, index=False)

    # ✅ Save strategy performance summary (optional)
    if summary:
        summary_path = os.path.join(path, f"{symbol}_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

    print(f"✅ Saved results for {symbol} to {path}")
