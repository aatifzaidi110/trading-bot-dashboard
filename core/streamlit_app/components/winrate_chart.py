# core/streamlit_app/components/winrate_chart.py

import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

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
    """
    Optional chart: overlay ML prediction confidence vs close price.
    """
    if "ml_prediction" not in df_signals.columns:
        return

    st.subheader("🤖 ML Confidence vs Price Outcome")
    df = df_signals[["Date", "ml_prediction", "close"]].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    
    chart = alt.Chart(df).transform_fold(
        ["ml_prediction", "close"],
        as_=["Metric", "Value"]
    ).mark_line().encode(
        x="Date:T",
        y="Value:Q",
        color="Metric:N",
        tooltip=["Date", "Metric", "Value"]
    ).properties(
        height=400,
        width="container",
        title="ML Confidence and Price Over Time"
    )

    st.altair_chart(chart, use_container_width=True)
