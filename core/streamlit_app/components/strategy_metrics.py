# core/streamlit_app/components/strategy_metrics.py

import streamlit as st
import pandas as pd

def render_strategy_metrics(perf_df: pd.DataFrame):
    if perf_df.empty:
        st.warning("No performance data found.")
        return

    st.subheader("📊 Strategy Performance Summary")
    st.dataframe(perf_df.rename(columns={
        "total_trades": "Trades",
        "wins": "Wins",
        "losses": "Losses",
        "win_rate": "WinRate",
        "Return (%)": "Return"
    }), use_container_width=True)
