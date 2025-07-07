# core/streamlit_app/components/signal_table.py

import streamlit as st
import pandas as pd

def render_signals(df: pd.DataFrame):
    if df.empty:
        st.info("No signals to display.")
        return

    st.subheader("🏆 Top 10 Trading Opportunities")
    styled_df = df[[
        "symbol", "Current Price", "signal", "confidence", "sentiment_score", "buzz",
        "return_pct", "sharpe_ratio"
    ]].rename(columns={
        "symbol": "Ticker", "signal": "Signal", "confidence": "Confidence",
        "sentiment_score": "Sentiment", "buzz": "Buzz", "return_pct": "Return (%)", "sharpe_ratio": "Sharpe"
    })

    st.dataframe(styled_df, use_container_width=True)
