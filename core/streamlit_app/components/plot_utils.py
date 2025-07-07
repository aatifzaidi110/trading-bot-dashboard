# streamlit_app/components/plot_utils.py

import streamlit as st
import pandas as pd
import plotly.express as px

def plot_signal_confidence(df: pd.DataFrame):
    if "Confidence" in df.columns and "Signal" in df.columns:
        fig = px.line(df, x="Date", y="Confidence", color="Signal", markers=True, title="Signal Confidence Over Time")
        st.plotly_chart(fig, use_container_width=True)

def plot_price_signals(df: pd.DataFrame):
    if "Signal" in df.columns:
        fig = px.line(df, x="Date", y="close", title="Price with Signals")
        buy = df[df["Signal"] == "BUY"]
        sell = df[df["Signal"].isin(["SELL", "TAKE_PROFIT", "STOP_LOSS"])]
        fig.add_scatter(x=buy["Date"], y=buy["close"], mode="markers", marker=dict(color="green", size=10), name="BUY")
        fig.add_scatter(x=sell["Date"], y=sell["close"], mode="markers", marker=dict(color="red", size=10), name="SELL")
        st.plotly_chart(fig, use_container_width=True)
