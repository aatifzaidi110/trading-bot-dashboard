# trading_bot/scripts/scan_top_tickers.py

import os
import json
import argparse
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from datetime import datetime
from trading_bot.utils.data_loader import load_price_data
from trading_bot.utils.ticker_list import get_top_tickers
from trading_bot.strategy.combo_strategy import ComboStrategy

# Save to CSV
OUTPUT_CSV = os.path.join("data", "top_signals.csv")
os.makedirs("data", exist_ok=True)

# Argument parser
parser = argparse.ArgumentParser(description="📈 Scan top tickers for trading signals")
parser.add_argument("--tickers", type=int, default=20, help="Limit number of tickers to scan")
parser.add_argument("--output", type=str, default=OUTPUT_CSV, help="Path to save CSV")
args = parser.parse_args()

tickers = get_top_tickers()[:args.tickers]
print(f"🔍 Scanning {len(tickers)} tickers...")

signals = []

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
            })
            signals.append(result)
    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

if signals:
    pd.DataFrame(signals).to_csv(args.output, index=False)
    print(f"✅ Top signals saved to: {args.output}")
else:
    print("⚠️ No signals generated.")
