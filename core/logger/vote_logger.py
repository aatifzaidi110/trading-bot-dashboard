# logger/vote_logger.py

import pandas as pd
import os
from datetime import datetime

def save_vote_log(vote_log, output_path):
    """
    Save the vote breakdown from the strategy to a CSV file.

    Parameters:
        vote_log (list of dict): The list of votes per timestamp.
        output_path (str): Path where the CSV file will be saved.
    """
    if not vote_log:
        print("⚠️ No vote log data to save.")
        return

    df = pd.DataFrame(vote_log)

    # Optional: Ensure Date is the first column and formatted
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"💾 Vote log saved to: {output_path}")
