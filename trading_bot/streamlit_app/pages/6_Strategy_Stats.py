# streamlit_app/pages/6_Strategy_Stats.py

import os
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="🏆 Strategy Leaderboard", layout="wide")
st.title("🏆 Strategy Leaderboard")


TRADE_LOG = "trades/trade_log.json"

def load_trades():
    if not os.path.exists(TRADE_LOG):
        return pd.DataFrame()
    with open(TRADE_LOG, "r") as f:
        try:
            data = json.load(f)
            return pd.DataFrame(data)
        except json.JSONDecodeError:
            return pd.DataFrame()

df = load_trades()

if df.empty:
    st.info("📭 No trades found.")
else:
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")
    df["entry"] = pd.to_numeric(df["entry"], errors="coerce")
    df["exit"] = pd.to_numeric(df["exit"], errors="coerce")
    df["profit_pct"] = ((df["exit"] - df["entry"]) / df["entry"]) * 100

    with st.expander("🔹 Raw Trade Table", expanded=False):
        st.dataframe(df, use_container_width=True)

    # === Win Rate Summary ===
    st.subheader("🏅 Win Rate by Symbol")
    summary = df.groupby(["symbol", "status"]).size().unstack(fill_value=0)
    summary["Total Trades"] = summary.sum(axis=1)
    summary["Win Rate (%)"] = (summary.get("WIN", 0) / summary["Total Trades"]) * 100
    st.dataframe(summary.sort_values("Win Rate (%)", ascending=False), use_container_width=True)

    # === Leaderboard ===
    st.subheader("🏆 Top Performing Tickers (by Avg Profit %)")
    leaderboard = df.groupby("symbol")["profit_pct"].mean().sort_values(ascending=False).reset_index()
    leaderboard.rename(columns={"profit_pct": "Avg Profit %"}, inplace=True)
    st.dataframe(leaderboard, use_container_width=True)

    # === Download Excel ===
    st.markdown("---")
    st.download_button(
        label="📥 Download Full Trade Log (Excel)",
        data=df.to_excel(index=False, engine='openpyxl'),
        file_name="trade_log_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
