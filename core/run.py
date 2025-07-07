# run.py

import argparse
from core.main import run_bot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the trading bot")
    parser.add_argument("mode", choices=["run", "backtest", "live"], help="Mode to run the bot")
    args = parser.parse_args()

    if args.mode == "run":
        run_bot()
    elif args.mode == "backtest":
        print("🔄 Backtest-only mode coming soon.")
    elif args.mode == "live":
        print("🚀 Live trading mode coming soon.")
