# streamlit_app/pages/6_Strategy_WinRate.py

import os
import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="🏆 Strategy Leaderboard", layout="wide")
st.title("🏆 Strategy Leaderboard")

TRADE_JSON = "trades/trade_log.json"

if not os.path.exists(TRADE_JSON):
    st.warning("No trade log found.")
    st.stop()

with open(TRADE_JSON) as f:
    try:
        trades = json.load(f)
    except json.JSONDecodeError:
        st.error("Invalid JSON format.")
        st.stop()

if not trades:
    st.info("No trades yet.")
    st.stop()

df = pd.DataFrame(trades)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# === Leaderboard ===
leaderboard = df.groupby("symbol").agg(
    Trades=("symbol", "count"),
    Wins=("result", lambda x: (x == "WIN").sum()),
    Losses=("result", lambda x: (x == "LOSS").sum()),
    WinRate=("result", lambda x: (x == "WIN").sum() / len(x)),
    AvgConfidence=("confidence", "mean"),
).sort_values("WinRate", ascending=False)

st.dataframe(leaderboard.style.format({"WinRate": "{:.1%}", "AvgConfidence": "{:.2f}"}), use_container_width=True)

# === Download leaderboard ===
csv = leaderboard.reset_index().to_csv(index=False).encode()
st.download_button("⬇️ Download Leaderboard CSV", csv, file_name="leaderboard.csv", mime="text/csv")
