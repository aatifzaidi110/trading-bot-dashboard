import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import plotly.graph_objects as go
from strategy.combo_strategy import ComboStrategy
from data.fetch_data import get_data

# Inputs
symbol = "AAPL"
from_date = "2022-01-01"
to_date = "2025-06-01"
output_path = f"visuals/combo_{symbol}_dashboard.html"

# Fetch and run strategy
df = get_data(symbol, from_date, to_date)
strategy = ComboStrategy()
df = strategy.generate_signals(df)

# Build chart
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df.index, y=df["close"],
    mode="lines", name="Close Price", line=dict(color="gray")
))

# Buy markers
buy_df = df[df["Signal"] == "BUY"]
fig.add_trace(go.Scatter(
    x=buy_df.index, y=buy_df["close"],
    mode="markers", name="BUY",
    marker=dict(color="green", size=8, symbol="triangle-up")
))

# Exit markers
exit_df = df[df["Signal"].isin(["SELL", "STOP_LOSS", "TAKE_PROFIT"])]
fig.add_trace(go.Scatter(
    x=exit_df.index, y=exit_df["close"],
    mode="markers", name="SELL/EXIT",
    marker=dict(color="red", size=8, symbol="triangle-down")
))

fig.update_layout(
    title=f"📊 {symbol} — Combo Strategy Dashboard",
    xaxis_title="Date", yaxis_title="Price (USD)",
    template="plotly_dark",
    legend=dict(x=0.01, y=0.99),
    height=600
)

# Export to HTML
fig.write_html(output_path)
print(f"✅ Chart saved to: {output_path}")