# trading_bot/utils/ticker_list.py

import os
from dotenv import load_dotenv

# Load optional env vars from .env if present
load_dotenv()

# === File fallback location ===
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'top_tickers.txt')

def get_top_tickers():
    """
    Returns a list of tickers:
    1. From config/top_tickers.txt (if present)
    2. From TICKER_LIST env var (comma-separated)
    3. Falls back to built-in NASDAQ list
    """
    # Option 1: Try config/top_tickers.txt
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return [line.strip().upper() for line in f if line.strip()]

    # Option 2: Try environment variable
    env_tickers = os.getenv("TICKER_LIST")
    if env_tickers:
        return [ticker.strip().upper() for ticker in env_tickers.split(",") if ticker.strip()]

    # Option 3: Built-in fallback
    return get_nasdaq_tickers()

def get_nasdaq_tickers():
    """Default fallback list of large-cap NASDAQ tickers"""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "NVDA", "META", "NFLX", "AMD", "INTC",
        "BABA", "PYPL", "ADBE", "PEP", "COST",
        "QCOM", "TMUS", "SBUX", "CSCO", "AVGO",
        "MRNA", "JD", "ZM", "CRWD", "DOCU",
        "SNOW", "PLTR", "COIN", "ROKU", "DDOG",
        "SHOP", "PDD", "LYFT", "UBER", "SPOT",
        "FSLY", "NET", "TWLO", "ASML", "BIDU"
    ]
