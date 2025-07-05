# streamlit_app/pages/3_Past_Trades.py

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime

TRADE_LOG = "trades/trade_log.json"
st.set_page_config(page_title="📒 Past Trades", layout="wide")
st.title("📒 Past Trades")

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

if os.path.exists(TRADE_LOG):
    try:
        with open(TRADE_LOG) as f:
            content = f.read().strip()
            trades = json.loads(content) if content else []
    except json.JSONDecodeError:
        trades = []
        st.warning("⚠️ Could not parse trade log.")

    if trades:
        for i, t in enumerate(trades):
            col1, col2, col3 = st.columns([2, 3, 3])
            with col1:
                st.write(f"**{t.get('symbol', '—')}** — `{t['Signal']}` ({t.get('confidence', '-')}/5)")
            with col2:
                st.write(f"📈 Entry: `{t.get('entry')}` | 🎯 Exit: `{t.get('exit')}`")
            with col3:
                if t["status"] == "PENDING":
                    t["status"] = st.radio(
                        f"Result for {t.get('symbol', '')}-{i}",
                        ["WIN", "LOSS", "EVEN"], key=f"status_{i}", horizontal=True
                    )

        safe_json_dump(trades, TRADE_LOG)
        st.success("✅ Trade outcomes updated.")
    else:
        st.info("📭 No trades logged yet.")
else:
    st.info("🗃️ No trade file found. Log a trade from the Top Signals tab.")
