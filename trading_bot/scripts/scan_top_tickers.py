# scripts/scan_top_tickers.py

import os
import pandas as pd
from strategy.combo_strategy import ComboStrategy
from utils.data_loader import load_data
from utils.sentiment_helper import get_sentiment_score  # Placeholder
from datetime import datetime

# ⚙️ Setup
TOP_TICKERS = [
    "AAPL", "MSFT", "TSLA", "AMZN", "NVDA", "GOOGL", "META", "NFLX", "AMD", "INTC",
    "PYPL", "SHOP", "PLTR", "SNOW", "COIN", "BIDU", "CRWD", "UBER", "PDD", "DKNG",
    "FSLR", "ROKU", "MELI", "DDOG", "SOUN", "RBLX", "LCID", "AFRM", "RIOT", "MARA",
    "SOFI", "CVNA", "WBD", "NKLA", "UPST", "FUBO", "CHPT", "DNA", "IONQ", "BIGC"
]  # You can expand this easily

OUTPUT_FILE = "data/top_signals.csv"
os.makedirs("data", exist_ok=True)

# 🔁 Loop through tickers
results = []

print(f"🔍 Scanning {len(TOP_TICKERS)} tickers...")

for symbol in TOP_TICKERS:
    try:
        df = load_data(symbol)
        strategy = ComboStrategy(name=f"{symbol}_Combo")
        df_signaled = strategy.generate_signals(df)

        if df_signaled.empty:
            continue

        last_row = df_signaled.iloc[-1]
        confidence = last_row.get("confidence_score", 0)
        signal = last_row.get("Signal", "HOLD")
        reason = last_row.get("Reason", "")
        summary = strategy.get_performance_summary()
        sentiment_score = get_sentiment_score(symbol)

        results.append({
            "Symbol": symbol,
            "Signal": signal,
            "Confidence": confidence,
            "Win Rate": round(summary.get("win_rate", 0), 2),
            "Sharpe": round(summary.get("Sharpe Ratio", 0), 2),
            "Drawdown": round(summary.get("Max Drawdown (%)", 0), 2),
            "Total Trades": summary.get("total_trades", 0),
            "Sentiment": sentiment_score,
            "Reason": reason,
            "Last Price": df["close"].iloc[-1],
            "Date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        print(f"⚠️ Error processing {symbol}: {e}")
        continue

# 🏆 Top 10 signals
df_results = pd.DataFrame(results)
df_results.sort_values(by=["Confidence", "Win Rate", "Sentiment"], ascending=False, inplace=True)
df_results.head(10).to_csv(OUTPUT_FILE, index=False)

print(f"✅ Top signals saved to: {OUTPUT_FILE}")
