import requests
from datetime import datetime
import csv
import os
from config import settings
from utils.logger import setup_logger

logger = setup_logger("OrderManager")

def execute_trade(symbol, signal):
    if signal not in ("BUY", "SELL"):
        logger.info(f"{symbol}: No trade executed (signal: {signal})")
        return

    side = "buy" if signal == "BUY" else "sell"

    url = f"{settings.ALPACA_BASE_URL}/v2/orders"
    headers = {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "symbol": symbol,
        "qty": 1,
        "side": side,
        "type": "market",
        "time_in_force": "gtc"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        order_data = response.json()
        logger.info(f"Executed {side.upper()} order for {symbol}: {order_data['id']}")
        _log_trade(symbol, signal, order_data['id'])
    except Exception as e:
        logger.error(f"Trade execution failed for {symbol}: {e}")

def _log_trade(symbol, signal, order_id):
    log_dir = "logs/trades"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "executed_trades.csv")
    log_exists = os.path.isfile(log_file)

    with open(log_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not log_exists:
            writer.writerow(["timestamp", "symbol", "signal", "order_id"])
        writer.writerow([datetime.now().isoformat(), symbol, signal, order_id])
