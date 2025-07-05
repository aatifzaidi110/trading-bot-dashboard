# 📊 Trading Bot Dashboard (Streamlit)

A modular, multipage Streamlit dashboard for scanning top stock tickers and generating signals using a combo strategy.

## 🚀 Features

- Signal scan via CLI or Streamlit
- Past trades logging
- Custom ticker list via `.env` or `config/top_tickers.txt`
- Modular strategy support

## 🧪 Run Scanner
```bash
python -m trading_bot.scripts.scan_top_tickers --tickers 10
