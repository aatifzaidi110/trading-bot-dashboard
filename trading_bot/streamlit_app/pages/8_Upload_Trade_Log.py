# streamlit_app/pages/8_Upload_Trade_Log.py

import os
import json
import streamlit as st

st.set_page_config(page_title="📤 Upload Trade Log", layout="centered")
st.title("📤 Upload Trade Log")

TRADE_JSON = "trades/trade_log.json"

uploaded = st.file_uploader("Choose a trade_log.json file", type="json")

if uploaded:
    try:
        data = json.load(uploaded)
        os.makedirs(os.path.dirname(TRADE_JSON), exist_ok=True)
        with open(TRADE_JSON, "w") as f:
            json.dump(data, f, indent=2)
        st.success("✅ Trade log imported successfully!")
    except Exception as e:
        st.error(f"❌ Error parsing file: {e}")
