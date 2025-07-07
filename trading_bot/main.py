from config import settings
from data import fetch_data
from strategy.sma_crossover import SMACrossoverStrategy
from execution import order_manager
from backtest import backtester
from utils.logger import setup_logger

logger = setup_logger()

def process_symbol(symbol):
    logger.info(f"Processing {symbol}...")
    df = fetch_data.get_data(symbol, settings.START_DATE, settings.END_DATE, settings.TIMEFRAME)
    if df is None or df.empty:
        logger.warning(f"No data for {symbol}")
        return

    strategy = SMACrossoverStrategy(
        short_window=settings.SMA_SHORT_WINDOW,
        long_window=settings.SMA_LONG_WINDOW
    )

    results = backtester.run_backtest(df, strategy, symbol)
    logger.info(f"{symbol} Backtest Results: {results}")

    signal = strategy.generate_signal(df)
    order_manager.execute_trade(symbol, signal)

def main():
    logger.info("Trading Bot Starting...")
    for symbol in settings.SYMBOLS:
        try:
            process_symbol(symbol)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")

if __name__ == "__main__":
    main()
