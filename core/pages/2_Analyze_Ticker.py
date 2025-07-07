import streamlit as st
from core.streamlit_app.sections.analyze_ticker import render_analyze_ticker

st.set_page_config(page_title="🔍 Analyze Any Ticker", layout="wide")
st.title("🔍 Analyze Any Ticker")

render_analyze_ticker()
