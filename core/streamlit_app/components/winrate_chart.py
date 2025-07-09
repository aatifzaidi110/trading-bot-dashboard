# core/streamlit_app/components/winrate_chart.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.utils.cleaning import clean_ml_chart_data  # ✅ import cleaning helper


def render_winrate_chart(perf_df: pd.DataFrame):
    if perf_df.empty:
        st.info("No strategy performance to show.")
        return

    fig = px.bar(
        perf_df,
        x="symbol",
        y="win_rate",
        text="win_rate",
        title="📊 Strategy WinRate by Ticker",
        labels={"win_rate": "Win Rate", "symbol": "Ticker"},
        color="win_rate",
        color_continuous_scale="Blues"
    )
    fig.update_traces(texttemplate='%{text:.2%}', textposition="outside")
    fig.update_layout(yaxis_tickformat=".0%", height=400)
    st.plotly_chart(fig, use_container_width=True)


def plot_ml_vs_actual(df_signals: pd.DataFrame):
    st.subheader("🤖 ML Confidence vs Price Outcome")

    df = clean_ml_chart_data(df_signals)  # ✅ clean data
    if df.empty:
        st.warning("Not enough data to plot ML confidence.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["ml_prediction"],
                             mode='lines+markers',
                             name='ML Prediction',
                             line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["close"],
                             mode='lines+markers',
                             name='Close Price',
                             line=dict(color='green')))

    fig.update_layout(
        title="ML Confidence and Price Over Time",
        xaxis_title="Date",
        yaxis_title="Value",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_candlestick_chart(df_signals: pd.DataFrame):
    st.subheader("📈 Candlestick Price Chart")

    required_cols = ["Date", "open", "high", "low", "close"]
    if not all(col in df_signals.columns for col in required_cols):
        st.warning("Candlestick data incomplete.")
        return

    df = df_signals.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    fig = go.Figure(data=[go.Candlestick(
        x=df["Date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])

    fig.update_layout(
        title="Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
