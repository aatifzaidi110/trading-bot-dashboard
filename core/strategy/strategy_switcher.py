# strategy/strategy_switcher.py

from config import settings

from core.strategy.rsi_strategy import RSIStrategy
from core.strategy.macd_strategy import MACDStrategy
from core.strategy.sma_crossover import SMACrossoverStrategy
from core.strategy.bollinger_strategy import BollingerStrategy
from core.strategy.combo_strategy import ComboStrategy
from core.strategy.ensemble_strategy import EnsembleStrategy
from core.strategy.ema200_trend import EMA200TrendStrategy
from core.strategy.ma_crossover_strategy import MACrossoverStrategy

def get_strategy_by_name(name: str):
    """
    Instantiates and returns the appropriate strategy class using parameters from settings.
    """
    name = name.lower()
    params = settings.STRATEGY_PARAMS

    if name == "rsi":
        return RSIStrategy(
            name="RSIStrategy",
            period=params.get("rsi_period", 14),
            oversold=params.get("rsi_threshold", 30),
            overbought=100 - params.get("rsi_threshold", 30)
        )

    elif name == "macd":
        return MACDStrategy(
            name="MACDStrategy",
            fast=params.get("macd_fast", 12),
            slow=params.get("macd_slow", 26),
            signal=params.get("macd_signal", 9)
        )

    elif name == "sma_crossover":
        return SMACrossoverStrategy(
            name="SMACrossoverStrategy",
            fast=params.get("sma_fast", 20),
            slow=params.get("sma_slow", 50)
        )

    elif name == "bollinger":
        return BollingerStrategy(
            name="BollingerStrategy",
            window=params.get("bollinger_window", 20),
            num_std_dev=params.get("bollinger_std", 2)
        )

    elif name == "combo":
        return ComboStrategy(
            name="ComboStrategy",
            sma_fast=params.get("sma_fast", 20),
            sma_slow=params.get("sma_slow", 50),
            rsi_period=params.get("rsi_period", 14),
            rsi_threshold=params.get("rsi_threshold", 30),
            macd_fast=params.get("macd_fast", 12),
            macd_slow=params.get("macd_slow", 26),
            macd_signal=params.get("macd_signal", 9),
            bollinger_window=params.get("bollinger_window", 20),
            bollinger_std=params.get("bollinger_std", 2),
            ema_period=params.get("ema_period", 200)
        )

    elif name == "ensemble":
        return EnsembleStrategy(name="EnsembleStrategy")

    elif name == "ema200":
        return EMA200TrendStrategy(
            name="EMA200TrendStrategy",
            ema_period=params.get("ema_period", 200),
            rsi_period=params.get("rsi_period", 14),
            rsi_oversold=params.get("rsi_threshold", 30),
            rsi_overbought=100 - params.get("rsi_threshold", 30)
        )

    elif name == "ma_crossover":
        return MACrossoverStrategy(
            name="MACrossoverStrategy",
            short_window=params.get("sma_fast", 20),
            long_window=params.get("sma_slow", 50)
        )

    else:
        raise ValueError(f"❌ Unknown strategy: {name}")
