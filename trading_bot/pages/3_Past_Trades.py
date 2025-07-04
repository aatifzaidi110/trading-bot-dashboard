import streamlit as st
from streamlit_app.sections.past_trades import render_past_trades

st.set_page_config(page_title="📒 Past Trades", layout="wide")
st.title("📒 Past Trades & Outcomes")

render_past_trades()
