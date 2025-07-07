# core/scripts/scan_top_tickers.py

import os
import sys
import json
import argparse
import pandas as pd
from datetime import datetime

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.utils.data_loader import load_price_data
from core.utils.ticker_list import get_top_tickers
from core.strategy.combo_strategy import ComboStrategy

# === CLI ARGUMENTS ===
parser = argparse.ArgumentParser(description="📈 Scan top tickers for trading signals")
parser.add_argument("--tickers", type=int, default=20, help="Limit number of tickers to scan")
parser.add_argument("--output", type=str, default="data/top_signals.csv", help="Path to save CSV")
parser.add_argument("--json", type=str, default="results/scan_results.json", help="Optional JSON export")
args = parser.parse_args()

# === Setup ===
tickers = get_top_tickers()[:args.tickers]
os.makedirs(os.path.dirname(args.output), exist_ok=True)
os.makedirs(os.path.dirname(args.json), exist_ok=True)

print(f"🔍 Scanning {len(tickers)} tickers...")

signals = []

# === Scan Logic ===
for symbol in tickers:
    df = load_price_data(symbol, period="6mo")
    if df is None or df.empty:
        continue

    try:
        strategy = ComboStrategy()
        result = strategy.generate(df)
        if result and result.get("signal") != "HOLD":
            result.update({
                "symbol": symbol,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "buzz": round(result.get("confidence", 0) / 2, 2),
                "return_pct": round(10 + result.get("confidence", 0) * 2.5, 2),  # Placeholder performance
                "sharpe_ratio": round(1.2 + result.get("confidence", 0) * 0.1, 2)  # Placeholder Sharpe
            })
            signals.append(result)
    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

# === Save Results ===
if signals:
    df_signals = pd.DataFrame(signals)
    df_signals.to_csv(args.output, index=False)

    with open(args.json, "w") as f:
        json.dump(signals, f, indent=2)

    print(f"✅ Signals saved to:\n📄 CSV: {args.output}\n🧾 JSON: {args.json}")
else:
    print("⚠️ No signals generated.")
