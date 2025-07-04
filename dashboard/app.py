# dashboard/app.py

import streamlit as st
import pandas as pd
import os
import sys

# Make sure Python can find 'config' inside 'trading_bot'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'trading_bot')))

from config import settings

# Streamlit page setup
st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")
st.title("🤖 Trading Bot Dashboard")

# === Layout with Tabs ===
tabs = st.tabs(["📈 Equity Curves", "📋 Executed Trades", "⚙️ Bot Configuration"])

# === TAB 1: Equity Curves ===
with tabs[0]:
    st.header("📈 Equity Curve Charts")
    equity_dir = os.path.join("data", "equity_curves")

    if os.path.exists(equity_dir) and os.listdir(equity_dir):
        for symbol in settings.SYMBOLS:
            equity_file = os.path.join(equity_dir, f"{symbol}.csv")
            if os.path.exists(equity_file):
                df = pd.read_csv(equity_file, parse_dates=["Date"])
                df = df.set_index("Date")
                st.subheader(symbol)
                st.line_chart(df["Equity"])
            else:
                st.warning(f"⚠️ No equity data found for {symbol}")
    else:
        st.info("ℹ️ No equity curve charts found yet. Run a backtest first.")

# === TAB 2: Executed Trades ===
with tabs[1]:
    st.header("📋 Executed Trades")

    trade_file = os.path.join("logs", "trades", "executed_trades.csv")
    if os.path.exists(trade_file):
        df = pd.read_csv(trade_file)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("Trade log exists but is currently empty.")
    else:
        st.info("No trades have been executed yet.")

# === TAB 3: Bot Configuration ===
with tabs[2]:
    st.header("⚙️ Bot Configuration")
    st.markdown(f"- **Strategy Name:** `{settings.STRATEGY_NAME}`")
    st.markdown(f"- **Symbols:** {', '.join(settings.SYMBOLS)}")
    st.markdown("**Strategy Parameters:**")
    st.json(settings.STRATEGY_PARAMS)