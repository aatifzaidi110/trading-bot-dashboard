# streamlit_app/pages/7_Reset_Logs.py

import os
import streamlit as st

st.set_page_config(page_title="🧹 Reset Logs", layout="centered")
st.title("🧹 Reset Trade Logs")

TRADE_JSON = "trades/trade_log.json"
TRADE_CSV = "logs/trade_log.csv"

st.warning("This will permanently delete all trade logs.")

if st.button("🗑️ Reset Trade Logs"):
    json_deleted = False
    csv_deleted = False

    if os.path.exists(TRADE_JSON):
        os.remove(TRADE_JSON)
        json_deleted = True

    if os.path.exists(TRADE_CSV):
        os.remove(TRADE_CSV)
        csv_deleted = True

    st.success(f"✅ Deleted: JSON = {json_deleted}, CSV = {csv_deleted}")
