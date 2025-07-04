# streamlit_app/pages/4_Options_Analysis.py

import os, sys
import streamlit as st
import numpy as np
import pandas as pd

# Add root path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)

from utils.data_loader import load_data
from strategy.combo_strategy import ComboStrategy
from utils.options_analyzer import get_options_chain, explain_greek

st.set_page_config(page_title="💼 Options Analysis", layout="wide")
st.title("💼 Options Chain & Spread Strategy")

# === Form ===
with st.form("options_form"):
    symbol = st.text_input("Enter Ticker (e.g. AAPL, MSFT)", value="AAPL")
    expiry = st.selectbox("Expiry Window", ["14D", "30D", "60D", "90D", "180D", "1Y"], index=3)
    run_btn = st.form_submit_button("Run Analysis")

if run_btn and symbol:
    st.markdown(f"### 📊 {symbol.upper()} — Analysis")
    df = load_data(symbol.upper(), period="6mo")

    if df is None:
        st.warning("⚠️ No price data available.")
    else:
        strategy = ComboStrategy()
        df_signaled = strategy.generate_signals(df)
        vote = strategy.vote_log[-1] if strategy.vote_log else {}
        st.write(f"**Signal:** `{vote.get('Signal', '-')}` | **Confidence:** `{vote.get('Confidence', '-')}/5`")
        st.line_chart(df_signaled.set_index("Date")["close"])

        # === Options Chain
        st.subheader("📈 Option Chain")
        chain, err = get_options_chain(symbol.upper())
        if err:
            st.error(err)
        else:
            st.write(f"Price: `{chain['current_price']}` | Expiry: `{chain['expiry']}`")

            st.subheader("📘 Calls")
            st.dataframe(chain["calls"][["strike", "lastPrice", "delta", "theta", "vega", "impliedVolatility", "moneyness"]], use_container_width=True)
            st.subheader("📕 Puts")
            st.dataframe(chain["puts"][["strike", "lastPrice", "delta", "theta", "vega", "impliedVolatility", "moneyness"]], use_container_width=True)

            # === Bull Call Spread Suggestion
            st.subheader("💡 Bull Call Spread Suggestion")
            try:
                calls = chain["calls"]
                atm = calls[calls["moneyness"] == "ATM"].iloc[0]
                otm = calls[calls["moneyness"] == "OTM"].iloc[0]
                cost = atm["lastPrice"] - otm["lastPrice"]
                reward = otm["strike"] - atm["strike"] - cost

                st.markdown(f"""
- Buy CALL `{atm['strike']}` @ ${atm['lastPrice']:.2f}  
- Sell CALL `{otm['strike']}` @ ${otm['lastPrice']:.2f}  
- **Max Cost:** ${cost:.2f} | **Max Reward:** ${reward:.2f}
                """)
            except:
                st.warning("⚠️ Spread suggestion not available.")

            # === Greek Definitions
            with st.expander("📖 Option Greek Explanations"):
                for greek in ["delta", "gamma", "theta", "vega", "impliedVolatility"]:
                    st.markdown(f"**{greek.title()}** — {explain_greek(greek)}")

            st.info("✅ High delta & low theta is better for buying. ATM = high liquidity.")
