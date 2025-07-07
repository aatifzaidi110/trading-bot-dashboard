# streamlit_app/pages/1_Top_10_Signals.py

import os, sys, json
import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf


# === Path Setup ===
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "trading_bot"))
sys.path.append(ROOT)

from core.utils.data_loader import load_data
from core.strategy.combo_strategy import ComboStrategy

# === Config ===
st.set_page_config(page_title="🏆 Top 10 Signals", layout="wide")
st.title("🏆 Top 10 Trading Opportunities")

SCAN_RESULTS = os.path.join(ROOT, "results", "scan_results.json")

if not os.path.exists(SCAN_RESULTS):
    st.warning("⚠️ No scan results found. Run `scan_nasdaq.py` first.")
    st.stop()

with open(SCAN_RESULTS) as f:
    results = json.load(f)

df = pd.DataFrame(results)

# === Add live price ===
def get_price(symbol):
    try:
        return round(yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1], 2)
    except Exception:
        return None

df["Current Price"] = df["symbol"].apply(get_price)

# === Filters ===
st.sidebar.markdown("## 🎯 Filter")
style = st.sidebar.selectbox("Trading Style", [
    "All", "Long-Term", "Swing", "Day Trade", "Scalping", "Options", "Short"
])
min_conf = st.sidebar.slider("Min Confidence", 0, 5, 3)
min_sent = st.sidebar.slider("Min Sentiment", -1.0, 1.0, 0.1)

filtered = df[
    (df["confidence"] >= min_conf) &
    (df["sentiment_score"] >= min_sent)
]

if style != "All":
    if style == "Long-Term": filtered = filtered[filtered["confidence"] >= 4]
    elif style == "Swing": filtered = filtered[filtered["buzz"] > 2]
    elif style == "Scalping": filtered = filtered[filtered["confidence"] >= 2]
    elif style == "Day Trade": filtered = filtered[filtered["return_pct"] > 0]
    elif style == "Options": filtered = filtered[filtered["confidence"] >= 3]
    elif style == "Short": filtered = filtered[filtered["sentiment_score"] < 0]

# === Display Table ===
top10 = filtered.sort_values(
    by=["confidence", "sentiment_score", "return_pct"], ascending=False
).head(10)

st.dataframe(
    top10[[
        "symbol", "Current Price", "signal", "confidence", "sentiment_score", "buzz",
        "return_pct", "sharpe_ratio"
    ]].rename(columns={
        "symbol": "Ticker", "signal": "Signal", "confidence": "Confidence",
        "sentiment_score": "Sentiment", "buzz": "Buzz",
        "return_pct": "Return (%)", "sharpe_ratio": "Sharpe"
    }),
    use_container_width=True
)

# === Field Info ===
with st.expander("ℹ️ Field Definitions"):
    st.markdown("""
| Field | Meaning |
|-------|---------|
| Signal | BUY / SELL / HOLD |
| Confidence | Number of bullish indicators (0–5) |
| trend_up | True = Price > 200 EMA |
| rsi_signal | RSI below oversold |
| macd_cross | MACD crossed signal line |
| bollinger_touch | Price touched lower band |
| sma_crossover | Fast SMA > Slow SMA |
| Return (%) | Past backtest return |
| Sharpe | Sharpe ratio of backtest |
| **Higher is better** for Confidence, Sentiment, Return, Sharpe |
    """)
