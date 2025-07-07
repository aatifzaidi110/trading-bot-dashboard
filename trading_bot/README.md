# 📈 Trading Bot Dashboard

A modular algorithmic trading dashboard built with **Streamlit**, designed for signal scanning, backtesting, strategy metrics, and trade logging.

---

## 🔧 Features

- ✅ **Multi-strategy support** (e.g., `ComboStrategy`)
- 🧠 Modular indicators (RSI, MACD, Bollinger, EMA, SMA)
- 📊 Confidence-based signal generation
- 💹 Historical data loading via Yahoo Finance
- 📤 Trade logging and performance tracking
- 📈 Strategy metrics, win/loss breakdowns
- 📅 Date & strategy filtering
- 🧪 Pytest-based unit testing
- ⚙️ Batch scanning via CLI with argparse

---

## 📁 Folder Structure

```bash
trading_bot/
├── streamlit_app/            # Streamlit UI
│   ├── dashboard.py
│   ├── pages/
│   │   ├── 1_Scanner.py
│   │   ├── 2_Trade_Log.py
│   │   ├── 3_Trade_Import.py
│   │   ├── 4_Trade_Metrics.py
│   │   ├── 5_Strategy_Stats.py
│   │   └── 6_Strategy_Metrics.py
│   └── components/           # Reusable chart/logic
│
├── strategy/
│   └── combo_strategy.py     # Entry/exit logic
│
├── indicators/
│   └── indicators.py         # Modular indicators
│
├── utils/
│   ├── data_loader.py
│   ├── performance_tracker.py
│   └── ticker_list.py
│
├── logger/
│   └── trade_logger.py
│
├── scripts/
│   └── scan_top_tickers.py   # CLI batch scanner
│
├── tests/                    # Pytest test cases
├── results/                  # Scan results (json)
├── trades/                   # trade_log.json
├── data/                     # Ticker CSVs
├── logs/
├── .env
└── README.md
