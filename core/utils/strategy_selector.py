# strategy/strategy_switcher.py

from config import settings
from core.strategy.rsi_strategy import RSIStrategy
from core.strategy.macd_strategy import MACDStrategy
from core.strategy.bollinger_strategy import BollingerStrategy
from core.strategy.ema200_trend import EMA200TrendStrategy
from core.strategy.combo_strategy import ComboStrategy
from core.strategy.ma_crossover_strategy import MACrossoverStrategy
from core.strategy.ensemble_strategy import EnsembleStrategy

from utils.strategy_selector import select_best_strategy

def get_strategy_by_name(name):
    if name.lower() == "rsi":
        return RSIStrategy()
    elif name.lower() == "macd":
        return MACDStrategy()
    elif name.lower() == "bollinger":
        return BollingerStrategy()
    elif name.lower() == "ema200":
        return EMA200TrendStrategy()
    elif name.lower() == "combo":
        return ComboStrategy()
    elif name.lower() == "sma_crossover":
        return MACrossoverStrategy()
    elif name.lower() == "ensemble":
        return EnsembleStrategy()
    elif name.lower() == "adaptive":
        # 🔁 Build and choose best dynamically
        strategies = [
            RSIStrategy(),
            MACDStrategy(),
            BollingerStrategy(),
            EMA200TrendStrategy(),
            ComboStrategy(),
            MACrossoverStrategy()
        ]
        return select_best_strategy(strategies)
    else:
        raise ValueError(f"❌ Unknown strategy name: {name}")