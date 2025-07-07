# scripts/export_combo_results.py

import os
import sys
import pandas as pd

# ✅ Ensure root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.strategy.combo_strategy import ComboStrategy
from core.utils.data_loader import load_data
from core.logger.performance_tracker import save_performance_summary # <-- fixed
from core.logger.vote_logger import save_vote_log                    # <-- fixed
from core.logger.trade_logger import save_vote_log

# 📁 Output dir
OUTPUT_DIR = "results/combo"
os.makedirs(OUTPUT_DIR, exist_ok=True)

symbols = ["AAPL", "MSFT", "TSLA", "AMZN", "SPY"]

for symbol in symbols:
    print(f"📈 Processing {symbol}...")

    # 📦 Load data
    df = load_data(symbol)

    # ✅ Apply strategy
    strategy = ComboStrategy()
    df_signaled = strategy.generate_signals(df)

    # ✅ Ensure proper 'Date' column
    df_signaled = df_signaled.copy()
    df_signaled["Date"] = df_signaled.index
    df_signaled.reset_index(drop=True, inplace=True)

    # 💾 Save signal file
    signal_path = os.path.join(OUTPUT_DIR, f"{symbol}_signals.csv")
    df_signaled.to_csv(signal_path, index=False)

    # 💾 Save votes
    vote_path = os.path.join(OUTPUT_DIR, f"{symbol}_votes.csv")
    save_vote_log(strategy.vote_log, vote_path)

    # 💾 Save summary
    summary = strategy.get_performance_summary()
    summary_path = os.path.join(OUTPUT_DIR, f"{symbol}_summary.json")
    save_performance_summary(summary, summary_path)

print(f"✅ Export complete. Files saved in: {os.path.abspath(OUTPUT_DIR)}")
