# streamlit_app/dashboard.py

import os, sys, json
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from datetime import datetime

# === Fix Python Path to Access strategy/ ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "trading_bot"))
sys.path.append(ROOT_DIR)

from strategy.combo_strategy import ComboStrategy  # ✅ Corrected import
from utils.data_loader import load_data
from utils.options_analyzer import get_options_chain, explain_greek

SCAN_RESULTS = "results/scan_results.json"
TRADE_LOG = "trades/trade_log.json"
os.makedirs("trades", exist_ok=True)

# === Streamlit Setup ===
st.set_page_config(page_title="📈 Trading Dashboard", layout="wide")
st.title("📊 Trading Signal Dashboard")

# === Safe JSON Dump ===
def safe_json_dump(data, path):
    def convert(o):
        if isinstance(o, (np.integer, np.int64)): return int(o)
        if isinstance(o, (np.floating, np.float64)): return float(o)
        if isinstance(o, (np.bool_)): return bool(o)
        if isinstance(o, (np.ndarray,)): return o.tolist()
        if isinstance(o, (pd.Timestamp, datetime)): return str(o)
        return o
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=convert)

# === Load & Filter Scan Results ===
if not os.path.exists(SCAN_RESULTS):
    st.error("❌ Run the scan script first.")
    st.stop()

with open(SCAN_RESULTS) as f:
    results = json.load(f)

df = pd.DataFrame(results)

def get_price(symbol):
    try:
        hist = yf.Ticker(symbol).history(period="1d")
        return round(hist["Close"].iloc[-1], 2) if not hist.empty else None
    except:
        return None

df["Current Price"] = df["symbol"].apply(get_price)
df.dropna(subset=["Current Price"], inplace=True)

# === Sidebar Filters ===
st.sidebar.markdown("## 🎯 Filter Signals")
style = st.sidebar.selectbox("Trading Style", ["All", "Long-Term", "Swing", "Day Trade", "Scalping", "Options", "Short"])
min_conf = st.sidebar.slider("Min Confidence", 0, 5, 3)
min_sent = st.sidebar.slider("Min Sentiment", -1.0, 1.0, 0.1)

filtered = df[(df["confidence"] >= min_conf) & (df["sentiment_score"] >= min_sent)]
if style != "All":
    if style == "Long-Term": filtered = filtered[filtered["confidence"] >= 4]
    elif style == "Swing": filtered = filtered[filtered["buzz"] > 2]
    elif style == "Scalping": filtered = filtered[filtered["confidence"] >= 2]
    elif style == "Day Trade": filtered = filtered[filtered["return_pct"] > 0]
    elif style == "Options": filtered = filtered[filtered["confidence"] >= 3]
    elif style == "Short": filtered = filtered[filtered["sentiment_score"] < 0]

top10 = filtered.sort_values(by=["confidence", "sentiment_score", "return_pct"], ascending=False).head(10)

# === Top 10 Display ===
st.subheader("🏆 Top 10 Trading Opportunities")
st.dataframe(
    top10[[
        "symbol", "Current Price", "signal", "confidence", "sentiment_score", "buzz",
        "return_pct", "sharpe_ratio"
    ]].rename(columns={
        "symbol": "Ticker", "signal": "Signal", "confidence": "Confidence",
        "sentiment_score": "Sentiment", "buzz": "Buzz", "return_pct": "Return (%)", "sharpe_ratio": "Sharpe"
    }),
    use_container_width=True
)

# === Ticker Deep Dive ===
st.subheader("🔎 Ticker Deep Analysis")
selected = st.selectbox("Choose a Ticker", top10["symbol"].unique() if not top10.empty else [])

if selected:
    df_selected = load_data(selected)
    strategy = ComboStrategy()
    df_signals = strategy.generate_signals(df_selected)
    vote = strategy.vote_log[-1] if strategy.vote_log else {}

    if vote:
        price = vote.get("Price", 0)
        entry, stop, target = price, round(price * 0.98, 2), round(price * 1.04, 2)

        st.markdown(f"### {selected} — **{vote['Signal']}**")
        st.write(f"**Confidence:** {vote['Confidence']}/5")
        st.write(f"**Entry:** {entry} | **Stop:** {stop} | **Target:** {target}")
        st.json(vote)

        st.line_chart(df_signals.set_index("Date")["close"])

        if st.button("✅ Mark as Traded"):
            trade_log = []
            if os.path.exists(TRADE_LOG):
                try:
                    trade_log = json.load(open(TRADE_LOG))
                except:
                    pass

            trade_log.append({
                "symbol": selected,
                "timestamp": str(datetime.now()),
                "entry": entry,
                "stop_loss": stop,
                "target": target,
                "confidence": vote.get("Confidence", 0),
                "signal": vote.get("Signal", "UNKNOWN"),
                "status": "PENDING"
            })
            safe_json_dump(trade_log, TRADE_LOG)
            st.success("✅ Trade saved.")

# === Past Trades Section ===
st.subheader("📒 Past Trades")

if os.path.exists(TRADE_LOG):
    try:
        with open(TRADE_LOG) as f:
            trades = json.load(f)
    except:
        trades = []

    df_trades = pd.DataFrame(trades)
    if not df_trades.empty:
        df_trades["timestamp"] = pd.to_datetime(df_trades["timestamp"])
        df_trades.sort_values(by="timestamp", ascending=False, inplace=True)

        st.dataframe(df_trades, use_container_width=True)

        with st.sidebar:
            st.markdown("### 💾 Export")
            st.download_button("📤 Export Trades", df_trades.to_csv(index=False), "trades.csv")
            if st.button("🧹 Reset Trade Log"):
                open(TRADE_LOG, "w").write("[]")
                st.success("✅ Cleared trade_log.json")

# === Adhoc Ticker Scanner ===
st.subheader("🔍 Analyze Any Ticker")

with st.form("lookup"):
    adhoc_symbol = st.text_input("Enter Ticker (e.g. AAPL)")
    expiry = st.selectbox("Expiry", ["14D", "30D", "60D", "90D", "180D", "1Y"])
    show_options = st.checkbox("Show Option Chain", value=True)
    run_btn = st.form_submit_button("Run Analysis")

if run_btn and adhoc_symbol:
    data = load_data(adhoc_symbol.upper(), period="6mo")
    if data is None:
        st.warning(f"⚠️ No data for {adhoc_symbol.upper()}")
    else:
        strategy = ComboStrategy()
        signals = strategy.generate_signals(data)
        vote = strategy.vote_log[-1] if strategy.vote_log else {}

        st.write(f"**Signal:** `{vote.get('Signal', 'N/A')}` | **Confidence:** `{vote.get('Confidence', 'N/A')}/5`")
        st.json(vote)
        st.line_chart(signals.set_index("Date")["close"])

        st.subheader("📉 Backtest Summary")
        st.write(strategy.get_performance_summary())

        st.download_button(
            "📤 Export Report", signals.to_csv(index=False),
            file_name=f"{adhoc_symbol}_report.csv"
        )

        if show_options:
            st.subheader("💼 Options Chain")
            chain_data, err = get_options_chain(adhoc_symbol.upper())
            if err:
                st.error(err)
            else:
                st.dataframe(chain_data["calls"], use_container_width=True)
                st.dataframe(chain_data["puts"], use_container_width=True)
