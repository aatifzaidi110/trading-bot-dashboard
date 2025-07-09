# core/streamlit_app/components/winrate_chart.py

import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

def render_winrate_chart(perf_df: pd.DataFrame):
    """
    Render a bar chart showing strategy win rate by ticker.
    """
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
    """
    Overlay ML prediction confidence vs close price over time.
    """
    st.subheader("🤖 ML Confidence vs Price Outcome")

    # Required columns
    required_cols = ["Date", "ml_prediction", "close"]
    missing_cols = [col for col in required_cols if col not in df_signals.columns]

    if missing_cols:
        st.warning(f"Missing columns for ML chart: {missing_cols}")
        return

    # Prepare data safely
    df = df_signals[required_cols].copy()
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df["ml_prediction"] = pd.to_numeric(df["ml_prediction"], errors='coerce')
    df["close"] = pd.to_numeric(df["close"], errors='coerce')
    df.dropna(subset=["Date", "ml_prediction", "close"], inplace=True)

    if df.empty:
        st.info("No valid data available to display ML vs Price chart.")
        return

    # Build altair chart
    chart = alt.Chart(df).transform_fold(
        ["ml_prediction", "close"],
        as_=["Metric", "Value"]
    ).mark_line().encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Value:Q", title="Value"),
        color="Metric:N",
        tooltip=["Date:T", "Metric:N", "Value:Q"]
    ).properties(
        height=400,
        width="container",
        title="ML Confidence and Price Over Time"
    )

    st.altair_chart(chart, use_container_width=True)
