import os
import sys
import json
import pandas as pd
from datetime import datetime
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.strategy.combo_strategy import ComboStrategy
from core.utils.data_loader import load_data
from core.logger.performance_tracker import save_performance_summary
from core.logger.trade_logger import save_vote_log

FINNHUB_API_KEY = "TODO_PASTE_YOUR_API_KEY"
FINNHUB_BASE = "https://finnhub.io/api/v1"

# === Output Paths ===
OUTPUT_DIR = "results/daily_scan"
EXPORT_PATH = "results/scan_results.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Ticker List ===
TOP_TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AMD", "NFLX", "INTC",
    "PYPL", "QCOM", "BIDU", "ADBE", "SHOP", "UBER", "ROKU", "SOFI", "PLTR", "F",
    "NIO", "CHPT", "MARA", "RIOT", "TQQQ", "ARKK", "SNAP", "COIN", "DKNG", "RBLX"
]
ALL_TICKERS = list(set(TOP_TICKERS))

def get_sentiment(symbol):
    try:
        url = f"{FINNHUB_BASE}/news-sentiment?symbol={symbol}&token={FINNHUB_API_KEY}"
        r = requests.get(url)
        data = r.json()
        return {
            "sentiment_score": round(data.get("companyNewsScore", 0), 2),
            "buzz": data.get("buzz", {}).get("articlesInLastWeek", 0)
        }
    except:
        return {"sentiment_score": 0, "buzz": 0}

results = []

for symbol in ALL_TICKERS:
    try:
        print(f"🔎 Scanning {symbol}...")
        df = load_data(symbol)
        if df is None: continue

        strategy = ComboStrategy()
        df_signals = strategy.generate_signals(df)

        vote = strategy.vote_log[-1] if strategy.vote_log else {}
        passed = sum(1 for k in ["trend_up", "rsi_signal", "macd_cross", "bollinger_touch", "sma_crossover"] if vote.get(k) is True)
        
        signal = vote.get("Signal", "HOLD")
        sentiment = get_sentiment(symbol)
        perf = strategy.get_performance_summary()

        df_signals.to_csv(f"{OUTPUT_DIR}/{symbol}_signals.csv", index=False)
        save_vote_log(strategy.vote_log, f"{OUTPUT_DIR}/{symbol}_votes.csv")
        save_performance_summary(perf, f"{OUTPUT_DIR}/{symbol}_summary.json")

        results.append({
            "symbol": symbol,
            "signal": signal,
            "confidence": int(passed),
            "confidence_ratio": f"{passed}/5",
            "sentiment_score": sentiment["sentiment_score"],
            "buzz": sentiment["buzz"],
            "return_pct": perf.get("Return (%)", 0),
            "sharpe_ratio": perf.get("Sharpe Ratio", 0),
            "drawdown": perf.get("Max Drawdown (%)", 0),
            "trades": perf.get("total_trades", 0),
            "win_rate": perf.get("win_rate", 0),
            "strategy": "ComboStrategy",
            "notes": "AutoScan"
        })

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")

# === Save JSON
with open(EXPORT_PATH, "w") as f:
    json.dump(results, f, indent=2, default=str)

print("✅ Scan complete. Results saved.")
