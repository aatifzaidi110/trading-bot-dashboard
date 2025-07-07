# streamlit_app/dashboard.py

import sys, os, json, time
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from datetime import datetime

# === PATH SETUP ===
# Add root directory to path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# === Core Imports ===
from core.strategy.combo_strategy import ComboStrategy
from core.utils.data_loader import load_data
from core.utils.equity_curve import load_equity_curves
from core.utils.options_analyzer import get_options_chain
from core.models.model_runner import enhance_with_ml  # ML stub

# === UI Components ===
from core.streamlit_app.components.signal_table import render_signals
from core.streamlit_app.components.strategy_metrics import render_strategy_metrics
from core.streamlit_app.components.trade_plot import render_trade_history
from core.streamlit_app.components.winrate_chart import render_winrate_chart
from core.streamlit_app.components.winrate_chart import plot_ml_vs_actual
...
plot_ml_vs_actual(df_signals)


# === Constants & Setup ===
SCAN_RESULTS = "results/scan_results.json"
TRADE_LOG = "trades/trade_log.json"
PERF_LOG = "logs/performance_log.json"

os.makedirs("trades", exist_ok=True)

# === Streamlit Setup ===
st.set_page_config(page_title="📈 Trading Dashboard", layout="wide")
st.title("📊 Trading Signal Dashboard")

# 🔁 Auto-refresh every 30s
st_autorefresh = st.empty()
if st_autorefresh.button("🔄 Refresh Now"):
    st.experimental_rerun()
st_autorefresh.empty()
st.experimental_set_query_params(refresh=str(time.time()))

# === Load JSON safely ===
def safe_json(path, fallback=[]):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return fallback

# === Load Data ===
results = safe_json(SCAN_RESULTS)
if not results:
    st.warning("⚠️ No scan results found. Run the bot first.")
    st.stop()

df = pd.DataFrame(results)

# === Add Current Prices ===
def get_price(symbol):
    try:
        price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
        return round(price, 2)
    except:
        return None

df["Current Price"] = df["symbol"].apply(get_price)
df.dropna(subset=["Current Price"], inplace=True)

# === Sidebar Filters ===
st.sidebar.header("🎯 Filter Signals")
style = st.sidebar.selectbox("Trading Style", ["All", "Swing", "Day", "Options", "Short"])
min_conf = st.sidebar.slider("Min Confidence", 0, 5, 3)
df = df[df["confidence"] >= min_conf]

# Apply style filter
if style == "Swing":
    df = df[df["buzz"] > 2]
elif style == "Day":
    df = df[df["return_pct"] > 0]
elif style == "Options":
    df = df[df["confidence"] >= 3]
elif style == "Short":
    df = df[df["sentiment_score"] < 0]

# === Show Top Opportunities ===
top10 = df.sort_values(by=["confidence", "sentiment_score", "return_pct"], ascending=False).head(10)
st.subheader("🏆 Top 10 Trading Opportunities")
render_signals(top10)

# === Deep Dive on Selected Ticker ===
st.subheader("🔎 Deep Dive")
selected = st.selectbox("Choose a Ticker", top10["symbol"].unique() if not top10.empty else [])
if selected:
    df_selected = load_data(selected, period="6mo")
    df_selected = enhance_with_ml(df_selected)  # 🧠 ML plugin hook

    strategy = ComboStrategy()
    df_signals = strategy.generate_signals(df_selected)

    vote = strategy.vote_log[-1] if strategy.vote_log else {}
    if vote:
        price = vote.get("Price", 0)
        st.markdown(f"### {selected} — **{vote['Signal']}**")
        st.write(f"**Confidence:** {vote['Confidence']}/5")
        st.json(vote)
        plot_trade_history(df_signals)

# === Equity Curve Comparison ===
st.subheader("📈 Equity Curve Comparison")
eq_df = load_equity_curves(top10["symbol"].tolist())
if not eq_df.empty:
    st.line_chart(eq_df.set_index("Date"))

# === Strategy Metrics ===
if os.path.exists(PERF_LOG):
    try:
        perf_df = pd.read_json(PERF_LOG)
        st.subheader("📊 Strategy Metrics")
        render_strategy_metrics(perf_df)
        render_winrate_chart(perf_df)
    except:
        st.warning("⚠️ Could not read performance_log.json")

# === Export Section ===
st.sidebar.markdown("### 💾 Export")
if os.path.exists(TRADE_LOG):
    trade_data = safe_json(TRADE_LOG)
    df_trades = pd.DataFrame(trade_data)
    if not df_trades.empty:
        st.sidebar.download_button("📤 Export Trades", df_trades.to_csv(index=False), "trades.csv")
