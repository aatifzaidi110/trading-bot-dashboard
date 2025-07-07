import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_trade_history(df: pd.DataFrame):
    if df.empty or "Signal" not in df.columns:
        st.warning("No signal data to plot.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["close"], mode="lines", name="Price"))

    # Highlight buy/sell/exit points
    buy = df[df["Signal"] == "BUY"]
    sell = df[df["Signal"].str.contains("STOP|EXIT", na=False)]

    fig.add_trace(go.Scatter(
        x=buy["Date"],
        y=buy["close"],
        mode="markers",
        name="BUY",
        marker=dict(color="green", size=10, symbol="triangle-up")
    ))

    fig.add_trace(go.Scatter(
        x=sell["Date"],
        y=sell["close"],
        mode="markers",
        name="SELL",
        marker=dict(color="red", size=10, symbol="triangle-down")
    ))

    fig.update_layout(
        title="📈 Price & Trade Signals",
        xaxis_title="Date",
        yaxis_title="Price",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)
