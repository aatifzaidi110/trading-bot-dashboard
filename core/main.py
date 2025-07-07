# main.py

import os
import sys
import time
import logging
import schedule

from datetime import datetime
from core.config import settings
from core.utils.dashboard_generator import generate_dashboard
from core.utils.performance_tracker import update_performance_metrics
from core.utils.equity_curve import save_equity_curve
from core.logger.trade_logger import log_trade
from core.execution import order_manager
from core.data import fetch_data
from core.strategy.strategy_switcher import get_strategy_by_name
from backtest.backtester import run_backtest

# ------------------ Logging Setup ------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ------------------ Cleanup Logs ------------------

def cleanup_logs():
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

# ------------------ Main Trading Loop ------------------

def run_bot():
    logging.info("🚀 Running Trading Bot...")

    for symbol in settings.SYMBOLS:
        logging.info(f"▶️ Processing symbol: {symbol}")

        df = fetch_data.get_data(
            symbol,
            start_date=settings.START_DATE,
            end_date=settings.END_DATE,
            timeframe=settings.TIMEFRAME
        )

        if df is None or df.empty:
            logging.warning(f"⚠️ No data for {symbol}. Skipping.")
            continue

        strategy = get_strategy_by_name(settings.STRATEGY_NAME)
        logging.info(f"📌 Using strategy: {strategy.name}")

        try:
            summary = run_backtest(strategy, symbol, period="6mo", interval=settings.TIMEFRAME, plot=False)
            update_performance_metrics(symbol, summary)
            save_equity_curve(symbol, df)
        except Exception as e:
            logging.error(f"❌ Backtest failed for {symbol}: {e}")
            continue

        try:
            signal = strategy.generate_signal(df)
            logging.info(f"🔁 Signal for {symbol}: {signal}")
            log_trade(datetime.now(), df["close"].iloc[-1], signal, "LIVE", df["close"].iloc[-1])
            order_manager.execute_trade(symbol, signal)
        except Exception as e:
            logging.error(f"❌ Execution failed for {symbol}: {e}")

    generate_dashboard()
    logging.info("✅ Bot finished successfully.\n")

# ------------------ Scheduler ------------------

schedule.every().day.at("16:01").do(run_bot)

# ------------------ Entry Point ------------------

if __name__ == "__main__":
    cleanup_logs()

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
