# streamlit_app/pages/5_Strategy_Stats.py

import os
import json
import streamlit as st
import pandas as pd

from utils.performance_tracker import save_performance_summary

st.set_page_config(page_title="📊 Strategy Overview", layout="wide")
st.title("📊 Strategy Performance Summary")

TRADE_JSON = "trades/trade_log.json"

if not os.path.exists(TRADE_JSON):
    st.warning("No trade log found.")
    st.stop()

with open(TRADE_JSON) as f:
    try:
        trades = json.load(f)
    except json.JSONDecodeError:
        st.error("Failed to load JSON.")
        st.stop()

if not trades:
    st.info("No trades recorded yet.")
    st.stop()

# Create DataFrame
df = pd.DataFrame(trades)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# === Filters ===
col1, col2, col3 = st.columns(3)

with col1:
    date_filter = st.date_input("📅 Filter by Date", [])
with col2:
    signal_filter = st.multiselect("🎯 Filter by Signal", df["signal"].unique())
with col3:
    ticker_filter = st.multiselect("💹 Filter by Ticker", df["symbol"].unique())

# === Apply filters ===
if date_filter:
    df = df[df["date"].isin(date_filter)]
if signal_filter:
    df = df[df["signal"].isin(signal_filter)]
if ticker_filter:
    df = df[df["symbol"].isin(ticker_filter)]

# === Summary Metrics ===
col1, col2, col3 = st.columns(3)
col1.metric("Total Trades", len(df))
col2.metric("Win %", f"{(df['result'] == 'WIN').mean() * 100:.1f}%" if "result" in df else "N/A")
col3.metric("Avg Confidence", f"{df['confidence'].mean():.2f}" if "confidence" in df else "N/A")

# === Table ===
st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)

# === Export ===
if st.download_button("⬇️ Export CSV", df.to_csv(index=False).encode(), file_name="strategy_summary.csv"):
    st.success("Exported successfully.")
