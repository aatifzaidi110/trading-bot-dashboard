import sys, os, json, time
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from datetime import datetime

# === PATH SETUP ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# === Core Imports ===
from core.strategy.combo_strategy import ComboStrategy
from core.utils.data_loader import load_data
from core.utils.equity_curve import load_equity_curves
from core.utils.options_analyzer import get_options_chain
from core.models.model_runner import enhance_with_ml

# === UI Components ===
from core.streamlit_app.components.signal_table import render_signals
from core.streamlit_app.components.strategy_metrics import render_strategy_metrics
from core.streamlit_app.components.trade_plot import render_trade_history
from core.streamlit_app.components.winrate_chart import render_winrate_chart, plot_ml_vs_actual

# === Constants ===
OT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
SCAN_RESULTS = os.path.join(ROOT_DIR, "core", "results", "scan_results.json")
TRADE_LOG = os.path.join(ROOT_DIR, "core", "trades", "trade_log.json")
PERF_LOG = os.path.join(ROOT_DIR, "core", "logs", "performance_log.json")

os.makedirs("trades", exist_ok=True)

st.set_page_config(page_title="📈 Trading Dashboard", layout="wide")
st.title("📊 Advanced Trading Dashboard")

# === Refresh Button ===
if st.button("🔄 Refresh Now"):
    st.rerun()

# === Utility ===
def safe_json(path, fallback=[]):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Failed to load {path}: {e}")
        return fallback

def get_price(symbol):
    try:
        price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
        return round(price, 2)
    except:
        return None

# === Load Data ===
results = safe_json(SCAN_RESULTS)
if not results:
    st.warning("⚠️ No scan results found. Run the bot first.")
    st.stop()

df = pd.DataFrame(results)
df["current_price"] = df["symbol"].apply(get_price)
df.dropna(subset=["current_price"], inplace=True)

# === Sidebar Filters ===
st.sidebar.header("🎯 Filter")
style = st.sidebar.selectbox("Trading Style", ["All", "Swing", "Day", "Scalping", "Options", "Short"])
min_conf = st.sidebar.slider("Min Confidence", 0, 5, 3)
selected_symbols = st.sidebar.multiselect("Select Tickers", sorted(df["symbol"].unique()), default=list(df["symbol"].unique()))
available_signals = df["signal"].unique().tolist() if "signal" in df.columns else []
default_signals = [s for s in ["BUY", "SELL"] if s in available_signals]

signal_type = st.sidebar.multiselect("Signal Type", available_signals, default=default_signals)

suggested_strategies = st.sidebar.multiselect("Suggested Strategy", df["suggested_strategy"].unique() if "suggested_strategy" in df.columns else [], default=df["suggested_strategy"].unique() if "suggested_strategy" in df.columns else [])

# === Full Indicator Set ===
available_indicators = sorted(set(k for row in df["indicators"] for k in row.keys()))
indicator_filter = st.sidebar.multiselect("Indicators to Show", available_indicators, default=["RSI", "MACD", "EMA200"])

# === Indicator Tooltips ===
INDICATOR_INFO = {
    "RSI": "Relative Strength Index – >70: Overbought, <30: Oversold.",
    "MACD": "MACD > Signal → Bullish momentum.",
    "EMA200": "Long-term trend filter.",
    "SMA50": "Medium-term trend indicator.",
    "Bollinger Lower": "Volatility bottom. Reversal sign.",
    "Bollinger Upper": "Volatility top. Reversal sign.",
    "VWAP": "Volume Weighted Avg Price – fair intraday value.",
    "Stochastic RSI": "Momentum of RSI. >80 overbought, <20 oversold.",
    "Supertrend": "Trend-following signal.",
    "Ichimoku": "Comprehensive trend framework.",
    "ATR": "Volatility range (used for stop levels).",
    "ADX": "Trend strength. >25 = strong trend.",
    "OBV": "On-Balance Volume – accumulation/distribution.",
    "IV": "Implied Volatility of options.",
    "Delta": "Price sensitivity to underlying move.",
    "Gamma": "Rate of change of delta.",
    "Put/Call Ratio": "Sentiment indicator. >1 = bearish, <1 = bullish."
}

# === Apply Filters ===
df = df[df["confidence"] >= min_conf]
df = df[df["symbol"].isin(selected_symbols)]

if style != "All":
    df = df[df["trade_type"] == style.lower()]
if "signal" in df.columns and signal_type:
    df = df[df["signal"].isin(signal_type)]
if "suggested_strategy" in df.columns and suggested_strategies:
    df = df[df["suggested_strategy"].isin(suggested_strategies)]

# === Trade Type Breakdown
st.subheader("📊 Filtered Signals")
TRADE_TYPES = ["scalping", "day", "swing", "long", "options", "short"]

for trade_type in TRADE_TYPES:
    group_df = df[df["trade_type"] == trade_type].sort_values(by="confidence", ascending=False)
    if group_df.empty:
        continue
    with st.expander(f"🚀 {trade_type.capitalize()} Signals ({len(group_df)})", expanded=False):
        for _, row in group_df.iterrows():
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown(f"### **{row['symbol']}**")
                st.write(f"📈 **Current Price:** ${row['current_price']}")
                st.write(f"🔒 **Confidence:** {row['confidence']}/5")
                st.write(f"🧠 **Sentiment Score:** {row.get('sentiment_score', 'N/A')}")
                st.write(f"📌 **Strategy:** {row.get('suggested_strategy', 'ComboStrategy')}")
                st.write(f"🛑 **Stop Loss:** {row.get('stop_loss', 'N/A')}")
                st.write(f"🎯 **Take Profit:** {row.get('take_profit', 'N/A')}")
                st.write(f"🧱 **Support:** {row.get('support', 'N/A')}")
                st.write(f"📉 **Resistance:** {row.get('resistance', 'N/A')}")

            with col2:
                st.markdown("**📊 Indicators**")
                indicators = row.get("indicators", {})
                for ind, val in indicators.items():
                    if ind in indicator_filter:
                        desc = INDICATOR_INFO.get(ind, "")
                        st.markdown(f"- 🧮 **{ind}**: `{val.get('value', 'N/A')}` → **Target:** `{val.get('target', 'N/A')}`")
                        if desc:
                            st.caption(desc)

                if trade_type == "options":
                    chain = get_options_chain(row["symbol"])
                    if chain is not None and not chain.empty:
                        st.markdown("**🧾 Option Chain Snapshot**")
                        st.dataframe(chain.head(3))

                news = row.get("news", [])
                if news:
                    st.markdown("📰 **News Headlines**")
                    for n in news[:3]:
                        st.write(f"- {n}")

# === Deep Dive
st.subheader("🔎 Deep Dive Analysis")
selected = st.selectbox("Select Ticker", df["symbol"].unique())
if selected:
    df_selected = load_data(selected, period="6mo")
    df_selected = enhance_with_ml(df_selected)
    strategy = ComboStrategy()
    df_signals = strategy.generate_signals(df_selected)
    plot_ml_vs_actual(df_signals)

    vote = strategy.vote_log[-1] if strategy.vote_log else {}
    if vote:
        st.markdown(f"### {selected} — **{vote['Signal']}**")
        st.write(f"Confidence: {vote['Confidence']}/5")
        st.json(vote)
        render_trade_history(df_signals)

# === Equity Curves
st.subheader("📈 Equity Curve Comparison")
eq_df = load_equity_curves(df["symbol"].tolist())
if not eq_df.empty:
    st.line_chart(eq_df.set_index("Date"))

# === Performance Summary
if os.path.exists(PERF_LOG):
    try:
        perf_df = pd.read_json(PERF_LOG)
        st.subheader("📊 Strategy Metrics")
        render_strategy_metrics(perf_df)
        render_winrate_chart(perf_df)
    except:
        st.warning("⚠️ Could not read performance_log.json")

# === Export
st.sidebar.markdown("### 💾 Export")
if os.path.exists(TRADE_LOG):
    trades = safe_json(TRADE_LOG)
    df_trades = pd.DataFrame(trades)
    if not df_trades.empty:
        st.sidebar.download_button("📤 Export Trades", df_trades.to_csv(index=False), "trades.csv")
