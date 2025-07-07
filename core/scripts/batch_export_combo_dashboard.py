# scripts/batch_export_combo_dashboard.py

import os
from core.trategy.combo_strategy import ComboStrategy
from core.utils.save_results import save_strategy_results
from data.data_loader import load_data  # Must exist and return a DataFrame with OHLCV
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYMBOLS = ["AAPL", "MSFT", "TSLA", "AMZN", "SPY"]  # Add/remove as needed

def export_all():
    for symbol in SYMBOLS:
        logger.info(f"📊 Exporting ComboStrategy for: {symbol}")

        try:
            df = load_data(symbol)
            strategy = ComboStrategy()
            df_with_signals = strategy.generate_signals(df)
            signal = strategy.generate_signal(df_with_signals)
            summary = strategy.performance_summary()

            save_strategy_results(
                symbol=symbol,
                strategy_name="combo",
                df=df_with_signals,
                summary=summary
            )

        except Exception as e:
            logger.error(f"❌ Failed for {symbol}: {e}")

if __name__ == "__main__":
    export_all()
