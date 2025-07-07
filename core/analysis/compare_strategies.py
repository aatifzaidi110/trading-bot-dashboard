from config import settings
from data import fetch_data
from backtest import backtester

from core.strategy.sma_crossover import SMACrossoverStrategy
from core.strategy.rsi_strategy import RSIStrategy
from core.strategy.macd_strategy import MACDStrategy
from core.strategy.bollinger_strategy import BollingerStrategy
from core.strategy.ema200_trend import EMA200Strategy
from core.strategy.combo_strategy import ComboStrategy

def compare_strategies(symbol):
    df = fetch_data.get_data(symbol, settings.START_DATE, settings.END_DATE, settings.TIMEFRAME)
    if df is None or df.empty:
        print(f"No data for {symbol}")
        return

    strategies = {
        "SMA_Crossover": SMACrossoverStrategy(20, 50),
        "RSI": RSIStrategy(14, 30, 70),
        "MACD": MACDStrategy(),
        "Bollinger": BollingerStrategy(),
        "EMA200": EMA200Strategy(),
        "Combo": ComboStrategy()
    }

    results = []
    for name, strategy in strategies.items():
        result = backtester.run_backtest(df, strategy, symbol=symbol, save_csv=False)
        result["Strategy"] = name
        results.append(result)

    print(f"\nBacktest Summary for {symbol}:\n")
    print("{:<15} {:<12} {:<12} {:<12} {:<14} {:<18}".format(
        "Strategy", "Final Value", "Return (%)", "Sharpe", "Max Drawdown", "Period"
    ))
    for r in results:
        print("{:<15} ${:<11} {:<12} {:<12} {:<14} {} to {}".format(
            r["Strategy"], r["Final Value"], r["Return (%)"], r["Sharpe Ratio"],
            f"{r['Max Drawdown (%)']}%", r["Start"], r["End"]
        ))

if __name__ == "__main__":
    compare_strategies("AAPL")
