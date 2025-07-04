# streamlit_app/Home.py

import streamlit as st

st.set_page_config(page_title="🧠 Trading Bot", layout="wide")

st.title("📈 Welcome to the Trading Signal App")
st.markdown("""
This app is a modular dashboard for:

- 🔍 **Adhoc analysis** using custom strategy signals
- 📊 **Top 10 filtered signals** based on daily scans
- 💼 **Options chain + spread strategy suggestions**
- 📒 **Track trades + log outcomes**

---

### 🧪 To run a scan:
- You can trigger the script manually via:
```bash
python scripts/scan_nasdaq.py
