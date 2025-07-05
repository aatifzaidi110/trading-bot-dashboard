# streamlit_app/pages/4_Strategy_Stats.py

import os
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="📊 Strategy Stats", layout="wide")
st.title("📊 Strategy Performance Summary")

TRADE_LOG = "trades/trade_log.json"

if os.path.exists(TRADE_LOG):
    try:
        with open(TRADE_LOG) as f:
            content = f.read().strip()
            trades = json.loads(content) if content else []
    except json.JSONDecodeError:
        trades = []
        st.warning(⚠️ Could not parse trade log.")

    if trades:
        df = pd.DataFrame(trades)

        df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")
        df["entry"] = pd.to_numeric(df["entry"], errors="coerce")
        df["exit"] = pd.to_numeric(df["exit"], errors="coerce")

        df["profit_pct"] = ((df["exit"] - df["entry"]) / df["entry"]) * 100

        summary = df.groupby(["symbol", "status"]).size().unstack(fill_value=0)
        summary["Total Trades"] = summary.sum(axis=1)
        summary["Win Rate (%)"] = (summary.get("WIN", 0) / summary["Total Trades"]) * 100

        st.dataframe(summary.sort_values("Win Rate (%)", ascending=False), use_container_width=True)

        st.markdown("---")
        st.subheader("📈 Profit Distribution")
        st.bar_chart(df.groupby("symbol")["profit_pct"].mean().sort_values(ascending=False))
    else:
        st.info("📭 No trades found.")
else:
    st.warning("🛑 trade_log.json not found. Run a scan or add trades first.")
