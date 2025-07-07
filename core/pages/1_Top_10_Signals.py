import streamlit as st
from streamlit_app.sections.top_signals import render_top_signals

st.set_page_config(page_title="📈 Top 10 Trading Signals", layout="wide")
st.title("🏆 Top 10 Trading Opportunities")

render_top_signals()
