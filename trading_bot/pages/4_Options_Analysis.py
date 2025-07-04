import streamlit as st
from streamlit_app.sections.options_analysis import render_options_analysis

st.set_page_config(page_title="💼 Options Chain", layout="wide")
st.title("💼 Options Chain & Strategy")

render_options_analysis()
