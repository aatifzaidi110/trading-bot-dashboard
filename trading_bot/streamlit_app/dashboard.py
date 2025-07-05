import os
import sys
import json
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import datetime

# === Project Path Setup ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from trading_bot.strategy.combo_strategy import ComboStrategy
from utils.data_loader import load_data
from utils.options_analyzer import get_options_chain, explain_greek

# === Safe JSON Dump for NumPy types ===
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

# === Streamlit Config ===
st.set_page_config(page_title="📈 Trading Dashboard", layout="wide")
st.title("📊 Trading Signal Dashboard")

# === Paths ===
SCAN_RESULTS = "results/scan_results.json"
TRADE_LOG = "trades/trade_log.json"
os.makedirs("trades", exist_ok=True)

# === Load Scan Results ===
if not os.path.exists(SCAN_RESULTS):
    st.error("❌ Run the scan script first.")
    st.stop()

with open(SCAN_RESULTS) as f:
    results = json.load(f)

df = pd.DataFrame(results)

# === Add Live Price + Drop Delisted ===
def get_price(symbol):
    try:
        hist = yf.Ticker(symbol).history(period="1d")
        if hist.empty:
            return None
        return round(hist["Close"].iloc[-1], 2)
    except:
        return None

df["Current Price"] = df["symbol"].apply(get_price)
df.dropna(subset=["Current Price"], inplace=True)

# === Sidebar Filters ===
st.sidebar.markdown("## 🎯 Filter")
style = st.sidebar.selectbox("Trading Style", [
    "All", "Long-Term", "Swing", "Day Trade", "Scalping", "Options", "Short"
])
min_conf = st.sidebar.slider("Min Confidence", 0, 5, 3)
min_sent = st.sidebar.slider("Min Sentiment", -1.0, 1.0, 0.1)

filtered = df[(df["confidence"] >= min_conf) & (df["sentiment_score"] >= min_sent)]

if style != "All":
    if style == "Long-Term": filtered = filtered[filtered["confidence"] >= 4]
    elif style == "Swing": filtered = filtered[filtered["buzz"] > 2]
    elif style == "Scalping": filtered = filtered[filtered["confidence"] >= 2]
    elif style == "Day Trade": filtered = filtered[filtered["return_pct"] > 0]
    elif style == "Options": filtered = filtered[filtered["confidence"] >= 3]
    elif style == "Short": filtered = filtered[filtered["sentiment_score"] < 0]

top10 = filtered.sort_values(by=["confidence", "sentiment_score", "return_pct"], ascending=False).head(10)

# === Top 10 Display ===
st.subheader("🏆 Top 10 Trading Opportunities")
st.dataframe(
    top10[[
        "symbol", "Current Price", "signal", "confidence", "sentiment_score", "buzz",
        "return_pct", "sharpe_ratio"
    ]].rename(columns={
        "symbol": "Ticker", "signal": "Signal", "confidence": "Confidence",
        "sentiment_score": "Sentiment", "buzz": "Buzz", "return_pct": "Return (%)", "sharpe_ratio": "Sharpe"
    }),
    use_container_width=True
)

# === Field Descriptions ===
with st.expander("ℹ️ Field Definitions"):
    st.markdown("""
| Field | Meaning |
|-------|---------|
| Signal | BUY / SELL / HOLD |
| Confidence | Number of bullish indicators (0–5) |
| trend_up | True = Price > 200 EMA |
| rsi_signal | RSI below oversold |
| macd_cross | MACD crossed signal line |
| bollinger_touch | Price touched lower band |
| sma_crossover | Fast SMA > Slow SMA |
| Return (%) | Past strategy backtest return |
| Sharpe | Sharpe ratio of backtest |
| **Higher values are better for Confidence, Sentiment, Return, Sharpe** |
    """)

# === Deep Dive Ticker ===
st.subheader("🔎 Ticker Deep Analysis")
selected = st.selectbox("Choose a Ticker", top10["symbol"].unique() if not top10.empty else [])

if selected:
    df_selected = load_data(selected)
    strategy = ComboStrategy()
    df_signals = strategy.generate_signals(df_selected)
    vote = strategy.vote_log[-1] if strategy.vote_log else {}

    if "Signal" in vote and "Confidence" in vote:
        price = vote.get("Price", 0)
        entry, stop, target = price, round(price * 0.98, 2), round(price * 1.04, 2)

        st.markdown(f"### {selected} — **{vote['Signal']}**")
        st.write(f"**Confidence:** {vote['Confidence']}/5")
        st.write(f"**Entry:** {entry} | **Stop:** {stop} | **Target:** {target}")
    else:
        st.warning("⚠️ Strategy did not return valid signal/confidence.")
        st.json(vote)

    st.json(vote)
    st.line_chart(df_signals.set_index("Date")["close"])

    if st.button("✅ Mark as Traded"):
        trade_log = []
        if os.path.exists(TRADE_LOG):
            with open(TRADE_LOG) as f:
                try: trade_log = json.load(f)
                except: trade_log = []

        trade_log.append({
            "symbol": selected,
            "date": str(datetime.now().date()),
            "entry": entry,
            "stop_loss": stop,
            "target": target,
            "confidence": vote.get("Confidence", 0),
            "signal": vote.get("Signal", "UNKNOWN"),
            "status": "PENDING"
        })

        safe_json_dump(trade_log, TRADE_LOG)
        st.success("📌 Trade saved.")

# === Past Trades Section ===
st.subheader("📒 Past Trades")
if os.path.exists(TRADE_LOG):
    try:
        with open(TRADE_LOG) as f:
            trades = json.load(f)
    except:
        trades = []

    for i, t in enumerate(trades):
        col1, col2, col3 = st.columns([2, 3, 3])
        with col1: st.write(f"**{t['symbol']}** — {t['signal']} ({t['confidence']}/5)")
        with col2: st.write(f"Entry: {t['entry']} | SL: {t['stop_loss']} | Target: {t['target']}")
        with col3:
            if t["status"] == "PENDING":
                t["status"] = st.radio(
                    f"Result for {t['symbol']}", ["WIN", "LOSS", "EVEN"],
                    key=f"trade_{i}", horizontal=True
                )
    safe_json_dump(trades, TRADE_LOG)

# === Adhoc Ticker Scanner ===
st.subheader("🔍 Analyze Any Ticker")
with st.form("lookup"):
    adhoc_symbol = st.text_input("Enter Ticker (e.g. AAPL)")
    expiry = st.selectbox("Expiry", ["14D", "30D", "60D", "90D", "180D", "1Y"])
    show_options = st.checkbox("Show Option Chain", value=True)
    run_btn = st.form_submit_button("Run Analysis")

if run_btn and adhoc_symbol:
    data = load_data(adhoc_symbol.upper(), period="6mo")
    if data is None:
        st.warning(f"⚠️ No data for {adhoc_symbol.upper()}")
    else:
        strategy = ComboStrategy()
        signals = strategy.generate_signals(data)
        vote = strategy.vote_log[-1] if strategy.vote_log else {}

        signal = vote.get("Signal", "N/A")
        confidence = vote.get("Confidence", "N/A")

        st.write(f"**Signal:** `{signal}` | **Confidence:** `{confidence}/5`")

        if "Signal" in vote:
            st.write(f"**Signal:** `{vote['Signal']}` | **Confidence:** `{vote.get('Confidence', 0)}/5`")
        st.json(vote)
        st.line_chart(signals.set_index("Date")["close"])

        st.subheader("📉 Backtest Summary")
        st.write(strategy.get_performance_summary())

        st.download_button(
            label="📤 Export Report",
            data=signals.to_csv(index=False),
            file_name=f"{adhoc_symbol}_report.csv",
            mime="text/csv"
        )

        # === Option Chain ===
        if show_options:
            st.subheader("💼 Options Chain & Strategy")
            chain_data, err = get_options_chain(adhoc_symbol.upper())
            if err:
                st.error(err)
            else:
                st.write(f"📈 Price: `{chain_data['current_price']}` | 📅 Expiry: `{chain_data['expiry']}`")

                st.subheader("📘 Calls")
                st.dataframe(chain_data["calls"][["strike", "lastPrice", "delta", "theta", "vega", "impliedVolatility", "moneyness"]], use_container_width=True)
                st.subheader("📕 Puts")
                st.dataframe(chain_data["puts"][["strike", "lastPrice", "delta", "theta", "vega", "impliedVolatility", "moneyness"]], use_container_width=True)

                st.markdown("### 📊 Bull Call Spread Suggestion")
                try:
                    calls = chain_data["calls"]
                    atm = calls[calls["moneyness"] == "ATM"].iloc[0]
                    otm = calls[calls["moneyness"] == "OTM"].iloc[0]
                    cost = atm["lastPrice"] - otm["lastPrice"]
                    reward = otm["strike"] - atm["strike"] - cost
                    st.markdown(f"""
- Buy CALL `{atm['strike']}` @ ${atm['lastPrice']:.2f}  
- Sell CALL `{otm['strike']}` @ ${otm['lastPrice']:.2f}  
- Max Cost: ${cost:.2f} | Max Reward: ${reward:.2f}
                    """)
                except:
                    st.warning("⚠️ Spread suggestion not available")

                with st.expander("📖 Greeks"):
                    for greek in ["delta", "gamma", "theta", "vega", "impliedVolatility"]:
                        st.markdown(f"**{greek.title()}** — {explain_greek(greek)}")

                st.info("✅ High delta & low theta = better for buying. ATM = best liquidity.")
