# main.py

import os
import sys
import time
import schedule
import logging

# Optional: reset logs before run
try:
    os.remove("logs/performance_log.json")
    print("🧹 Cleared old performance_log.json")
except FileNotFoundError:
    pass

try:
    os.remove("logs/trade_log.csv")
    print("🧹 Cleared old trade_log.csv")
except FileNotFoundError:
    pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from data import fetch_data
from strategy.strategy_switcher import get_strategy_by_name
from execution import order_manager
from backtest import backtester
from utils.equity_curve import save_equity_curve
from utils.dashboard_generator import generate_dashboard
from utils.performance_tracker import update_performance_metrics
from logger.trade_logger import log_trade

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_bot():
    logging.info("🚀 Running Trading Bot...")

    for symbol in settings.SYMBOLS:
        logging.info(f"▶️ Processing symbol: {symbol}")
        df = fetch_data.get_data(symbol, settings.START_DATE, settings.END_DATE, settings.TIMEFRAME)

        if df is None or df.empty:
            logging.warning(f"⚠️ No data for {symbol}. Skipping.")
            continue

        strategy_name = settings.STRATEGY_NAME.lower()
        logging.info(f"📌 Using strategy: {strategy_name}")
        strategy = get_strategy_by_name(strategy_name)

        try:
            result, equity_df = backtester.run_backtest(df.copy(), strategy, symbol)
            logging.info(f"📊 Backtest for {symbol}: {result}")
            update_performance_metrics(symbol, result)
            save_equity_curve(symbol, equity_df)
        except Exception as e:
            logging.error(f"❌ Backtest failed for {symbol}: {e}")
            continue

        try:
            signal = strategy.generate_signal(df)
            logging.info(f"🔁 Signal for {symbol}: {signal}")
            log_trade(symbol, signal, df)
            order_manager.execute_trade(symbol, signal)
        except Exception as e:
            logging.error(f"❌ Execution failed for {symbol}: {e}")

    generate_dashboard()
    logging.info("✅ Bot finished successfully.\n")

schedule.every().day.at("16:01").do(run_bot)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run_now":
        run_bot()
    else:
        logging.info("🕒 Waiting for scheduled run at 16:01 daily. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logging.info("🛑 Bot stopped by user.")