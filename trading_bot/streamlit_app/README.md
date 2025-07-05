# 📊 Streamlit Dashboard for Trading Bot

This directory contains the Streamlit frontend for interacting with your trading bot.

## Structure

| File | Description |
|------|-------------|
| `1_Top_10_Signals.py` | Shows the top 10 tickers by signal strength |
| `2_Analyze_Ticker.py` | Visualize signal + indicator breakdown for any ticker |
| `3_Past_Trades.py` | View previous trade logs (with filtering/export) |
| `4_Options_Analysis.py` | (Optional) Placeholder for options data |
| `5_Strategy_Stats.py` | Win-rate analysis per strategy and visual breakdown |
| `6_Strategy_Stats.py` | ⚠️ Duplicate — remove or rename to avoid Streamlit path conflicts |
| `7_Reset_Logs.py` | Reset button for clearing all logs safely |
| `8_Upload_Trade_Log.py` | Upload previous trade logs for analysis |
| `components/plot_utils.py` | Reusable plot logic (price chart, confidence etc) |

---

## Usage

Run the app:
```bash
streamlit run streamlit_app/dashboard.py
