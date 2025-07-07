# streamlit_app/pages/6_Strategy_Metrics.py

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px

# === Paths ===
TRADE_LOG_PATH = "trades/trade_log.json"

st.set_page_config(page_title="📈 Strategy Metrics", layout="wide")
st.title("📈 Strategy Performance Summary")

# === Load Trades ===
if not os.path.exists(TRADE_LOG_PATH):
    st.warning("⚠️ No trade log found.")
    st.stop()

with open(TRADE_LOG_PATH) as f:
    try:
        trades = json.load(f)
    except json.JSONDecodeError:
        st.error("❌ Invalid format in trade log.")
        st.stop()

if not trades:
    st.warning("🕳️ Trade log is empty.")
    st.stop()

# === DataFrame Setup ===
df = pd.DataFrame(trades)
df["timestamp"] = pd.to_datetime(df.get("timestamp", pd.to_datetime(df["date"], errors='coerce')))
df.sort_values("timestamp", inplace=True)
df["confidence"] = pd.to_numeric(df.get("confidence", 0), errors='coerce')
df["entry"] = pd.to_numeric(df.get("entry", 0), errors='coerce')
df["symbol"] = df["symbol"].str.upper()
df["status"] = df["status"].str.upper()

# === Sidebar Filters ===
st.sidebar.header("🔍 Filters")

# Date range
min_date, max_date = df["timestamp"].min(), df["timestamp"].max()
date_range = st.sidebar.date_input("Filter by date", [min_date, max_date])
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df = df[(df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)]

# Status and ticker
statuses = st.sidebar.multiselect("Status", sorted(df["status"].unique()), default=list(df["status"].unique()))
tickers = st.sidebar.multiselect("Ticker", sorted(df["symbol"].unique()), default=list(df["symbol"].unique()))
df = df[df["status"].isin(statuses) & df["symbol"].isin(tickers)]

# === Summary Stats ===
st.subheader("📊 Overview")
total = len(df)
wins = len(df[df["status"] == "WIN"])
losses = len(df[df["status"] == "LOSS"])
even = len(df[df["status"] == "EVEN"])
win_rate = round((wins / total) * 100, 2) if total else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Trades", total)
col2.metric("✅ Wins", wins)
col3.metric("❌ Losses", losses)
col4.metric("🎯 Win Rate", f"{win_rate} %")

# === Confidence vs. Win Rate ===
st.subheader("📈 Confidence vs. Win Rate")

conf_stats = df.groupby("confidence")["status"].value_counts().unstack().fillna(0)
conf_stats["Win Rate (%)"] = conf_stats.get("WIN", 0) / conf_stats.sum(axis=1) * 100
conf_stats = conf_stats.reset_index()

fig = px.line(conf_stats, x="confidence", y="Win Rate (%)", markers=True)
st.plotly_chart(fig, use_container_width=True)

# === Trades per Ticker ===
st.subheader("📌 Trades per Ticker")

ticker_counts = df["symbol"].value_counts().reset_index()
ticker_counts.columns = ["Ticker", "Trade Count"]
bar = px.bar(ticker_counts, x="Ticker", y="Trade Count", text="Trade Count")
st.plotly_chart(bar, use_container_width=True)

# === Raw Table View ===
st.subheader("📒 Filtered Trades")
st.dataframe(df, use_container_width=True)

# === Export Button ===
st.download_button(
    label="📤 Export to CSV",
    data=df.to_csv(index=False),
    file_name="strategy_metrics_filtered.csv",
    mime="text/csv"
)
# === Confidence Over Time ===
st.subheader("📉 Confidence Over Time")

conf_time = df[["timestamp", "confidence"]].dropna()
conf_time = conf_time.set_index("timestamp").resample("D").mean().dropna()

fig_conf_time = px.line(conf_time, y="confidence", title="Daily Avg Confidence")
st.plotly_chart(fig_conf_time, use_container_width=True)

# === Win/Loss Trend Over Time ===
st.subheader("📆 Win/Loss Daily Trend")

df["count"] = 1
freq = st.radio("🕒 Trend Frequency", ["Daily", "Weekly"], horizontal=True)
resample_freq = "W" if freq == "Weekly" else "D"

trend = df.groupby([pd.Grouper(key="timestamp", freq=resample_freq), "status"])["count"].sum().unstack().fillna(0)
trend = trend.rolling(2).mean()  # Smooth

fig_trend = px.line(trend, title="Daily Win/Loss Trend (3-day SMA)")
st.plotly_chart(fig_trend, use_container_width=True)

