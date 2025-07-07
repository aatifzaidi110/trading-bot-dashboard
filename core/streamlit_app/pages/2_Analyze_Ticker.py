# streamlit_app/pages/Analyze_Ticker.py

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import sys

from datetime import datetime

# === Add root for imports

# === Path Setup ===
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "trading_bot"))
sys.path.append(ROOT)

from utils.data_loader import load_data
from strategy.combo_strategy import ComboStrategy

from strategy.combo_strategy import ComboStrategy
from utils.data_loader import load_data
from utils.options_analyzer import get_options_chain, explain_greek

# === Utility for JSON-safe dumps
def safe_json_dump(data, path):
    def convert(o):
        if isinstance(o, (np.integer, np.int64)): return int(o)
        if isinstance(o, (np.floating, np.float64)): return float(o)
        if isinstance(o, (np.bool_)): return bool(o)
        if isinstance(o, (np.ndarray,)): return o.tolist()
        if isinstance(o, (pd.Timestamp, datetime)): return str(o)
        return o
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=convert)

# === Streamlit App ===
st.title("🔍 Analyze Any Ticker")

with st.form("lookup_form"):
    adhoc_symbol = st.text_input("Enter Ticker (e.g. AAPL, TSLA, PLTR)")
    expiry = st.selectbox("Select Expiry Window", ["14D", "30D", "60D", "90D", "180D", "1Y"])
    show_options = st.checkbox("📈 Show Option Chain", value=True)
    run_btn = st.form_submit_button("Run Analysis")

if run_btn and adhoc_symbol:
    adhoc_symbol = adhoc_symbol.upper()
    df = load_data(adhoc_symbol, period="6mo")
    
    if df is None or df.empty:
        st.error(f"⚠️ No data found for {adhoc_symbol}. It may be delisted or invalid.")
    else:
        strategy = ComboStrategy()
        df_signals = strategy.generate_signals(df)

        # ✅ Safe check for signal log
        if strategy.vote_log:
            vote = strategy.vote_log[-1]
            signal = vote.get("Signal", "N/A")
            confidence = vote.get("Confidence", 0)
            price = vote.get("Price", df_signals['close'].iloc[-1])
        else:
            st.warning("⚠️ No valid signal generated. This may be a data issue.")
            vote, signal, confidence, price = {}, "N/A", 0, df['close'].iloc[-1]

        st.markdown(f"### 📊 {adhoc_symbol} — **{signal}**")
        st.write(f"**Confidence:** {confidence}/5")
        st.write(f"**Entry Price:** {price:.2f} | **Stop Loss:** {price * 0.98:.2f} | **Target:** {price * 1.04:.2f}")
        st.json(vote)
        st.line_chart(df_signals.set_index("Date")["close"])

        # === Backtest Summary ===
        st.subheader("📉 Backtest Summary")
        st.write(strategy.get_performance_summary())

        # === Export Report ===
        st.download_button(
            label="📤 Export CSV",
            data=df_signals.to_csv(index=False),
            file_name=f"{adhoc_symbol}_report.csv",
            mime="text/csv"
        )

        # === Option Chain Analysis ===
        if show_options:
            st.subheader("💼 Options Chain & Strategy")

            chain_data, err = get_options_chain(adhoc_symbol)
            if err:
                st.error(err)
            else:
                st.write(f"📈 Current Price: `{chain_data['current_price']}` | 📅 Expiry: `{chain_data['expiry']}`")

                st.subheader("📘 Calls")
                st.dataframe(chain_data["calls"][["strike", "lastPrice", "delta", "theta", "vega", "impliedVolatility", "moneyness"]], use_container_width=True)

                st.subheader("📕 Puts")
                st.dataframe(chain_data["puts"][["strike", "lastPrice", "delta", "theta", "vega", "impliedVolatility", "moneyness"]], use_container_width=True)

                # === Bull Call Spread Suggestion ===
                st.markdown("### 📊 Spread Suggestion")
                try:
                    calls = chain_data["calls"]
                    atm = calls[calls["moneyness"] == "ATM"].iloc[0]
                    otm = calls[calls["moneyness"] == "OTM"].iloc[0]

                    cost = atm["lastPrice"] - otm["lastPrice"]
                    reward = otm["strike"] - atm["strike"] - cost
                    st.markdown(f"""
- **Buy Call** `{atm['strike']}` @ ${atm['lastPrice']:.2f}  
- **Sell Call** `{otm['strike']}` @ ${otm['lastPrice']:.2f}  
- 💰 **Max Cost:** ${cost:.2f}  
- 🎯 **Max Reward:** ${reward:.2f}
                    """)
                except:
                    st.warning("⚠️ Could not compute spread suggestion.")

                # === Explain Greeks ===
                with st.expander("📖 Option Greeks Explained"):
                    for greek in ["delta", "gamma", "theta", "vega", "impliedVolatility"]:
                        st.markdown(f"**{greek.title()}** — {explain_greek(greek)}")

                st.info("✅ High delta + low theta is preferred for buyers. ATM = best liquidity.")
