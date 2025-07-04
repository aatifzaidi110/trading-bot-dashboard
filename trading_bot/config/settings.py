# config/settings.py

# Currently selected strategy
STRATEGY_NAME = "ensemble" # Options: "sma_crossover", "rsi", "macd", "bollinger", "ema200", "combo"

# Symbols to process
SYMBOLS = ["AAPL", "MSFT", "TSLA", "AMZN", "SPY"]

# Global strategy parameters
STRATEGY_PARAMS = {
    "sma_fast": 20,
    "sma_slow": 50,
    "rsi_threshold": 30,
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bollinger_window": 20,
    "bollinger_std": 2,
    "ema_period": 200
}

# Backtest configuration
INITIAL_BALANCE = 10000
START_DATE = "2022-01-03"
END_DATE = "2025-05-30"

# Broker simulation
PAPER_TRADING = True

# Output settings
SAVE_TRADE_LOGS = True
SAVE_EQUITY_CURVES = True

# Data fetch resolution
TIMEFRAME = "1d"

# Alpaca credentials (replace for real trading)
ALPACA_API_KEY = "PKG70DDVK4FTZX4D7Q8O"        
ALPACA_SECRET_KEY = "myxtfO7sQe5NMao5DXaA09wOJGWsMgKaut9FRVSf"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"