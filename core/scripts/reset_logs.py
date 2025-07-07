# scripts/reset_logs.py

import os
import json
import pandas as pd

TRADE_LOG_JSON = "trades/trade_log.json"
TRADE_LOG_CSV = "logs/trade_log.csv"

def clear_file(path):
    if os.path.exists(path):
        open(path, "w").close()
        print(f"✅ Cleared: {path}")
    else:
        print(f"⚠️ File not found: {path}")

def reset_json(path):
    if os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f, indent=2)
        print(f"✅ Reset JSON: {path}")
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump([], f, indent=2)
        print(f"✅ Created and reset JSON: {path}")

if __name__ == "__main__":
    reset_json(TRADE_LOG_JSON)
    clear_file(TRADE_LOG_CSV)
