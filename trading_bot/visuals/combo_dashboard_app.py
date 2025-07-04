# visuals/combo_dashboard_app.py

import streamlit as st
import pandas as pd
import os
import plotly.graph_objs as go

RESULTS_DIR = "results/combo"
DEFAULT_SYMBOLS = [f.split("_")[0] for f in os.listdir(RESULTS_DIR) if f.endswith("_equity.csv")]
DEFAULT_SYMBOLS = sorted(set(DEFAULT_SYMBOLS))

st.set_page_config(page_title="Combo Strategy Dashboard", layout="wide")
st.title("🧠 Combo Strategy Performance Dashboard")

# --- Symbol Selector
symbol = st.selectbox("Select Symbol", DEFAULT_SYMBOLS)

# --- Load Data
equity_file = os.path.join(RESULTS_DIR, f"{symbol}_equity.csv")
votes_file = os.path.join(RESULTS_DIR, f"{symbol}_votes.csv")
trades_file = os.path.join("logs", f"{symbol}_trades.csv")

if not os.path.exists(equity_file) or not os.path.exists(votes_file):
    st.error("Missing result files for selected symbol.")
    st.stop()

df = pd.read_csv(equity_file, parse_dates=["Date"])
votes_df = pd.read_csv(votes_file, parse_dates=["Date"])
trades_df = pd.read_csv(trades_file, parse_dates=["Date"]) if os.path.exists(trades_file) else pd.DataFrame()

# --- Equity Chart with Signals
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close", line=dict(color="lightblue")))

signals = df[df["Signal"].isin(["BUY", "SELL", "TAKE_PROFIT", "STOP_LOSS"])]
colors = {"BUY": "green", "SELL": "red", "TAKE_PROFIT": "blue", "STOP_LOSS": "orange"}

for signal_type in signals["Signal"].unique():
    subset = signals[signals["Signal"] == signal_type]
    fig.add_trace(go.Scatter(
        x=subset["Date"],
        y=subset["Close"],
        mode="markers",
        name=signal_type,
        marker=dict(size=10, color=colors.get(signal_type, "gray")),
    ))

fig.update_layout(title=f"{symbol} - Price with Trade Signals", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- Vote Breakdown (stacked bar)
if "BUY" in votes_df and "SELL" in votes_df and "HOLD" in votes_df:
    vote_fig = go.Figure()
    for vote in ["BUY", "SELL", "HOLD"]:
        vote_fig.add_trace(go.Bar(
            x=votes_df["Date"],
            y=votes_df[vote],
            name=vote,
        ))

    vote_fig.update_layout(
        barmode="stack",
        title="🗳️ Strategy Votes Over Time",
        height=300
    )
    st.plotly_chart(vote_fig, use_container_width=True)
else:
    st.warning("📉 Voting data incomplete or missing.")

# --- Trade Log
if not trades_df.empty:
    st.subheader("🧾 Trade Log")
    st.dataframe(trades_df.tail(50))
else:
    st.info("No trade log found yet.")

# --- Performance Summary (from equity)
if "Equity" in df.columns:
    final_equity = df["Equity"].iloc[-1]
    start_equity = df["Equity"].iloc[0]
    return_pct = ((final_equity - start_equity) / start_equity) * 100

    st.metric("📈 Return (%)", f"{return_pct:.2f}%")
    st.metric("Final Equity", f"${final_equity:,.2f}")
