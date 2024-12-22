from typing import Dict, Type, List
from .strategy_interface import StrategyInterface
from .simple_ma_strategy import SimpleMAStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .combined_strategy import CombinedStrategy

class StrategyRegistry:
    """Registry for all available trading strategies"""
    _strategies: Dict[str, Type[StrategyInterface]] = {}
    
    @classmethod
    def register(cls, strategy_class: Type[StrategyInterface]) -> None:
        """Register a new strategy"""
        cls._strategies[strategy_class.__name__] = strategy_class
    
    @classmethod
    def get_strategy(cls, name: str) -> Type[StrategyInterface]:
        """Get strategy class by name"""
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found")
        return cls._strategies[name]
    
    @classmethod
    def get_all_strategies(cls) -> List[Dict]:
        """Get information about all registered strategies"""
        return [
            {
                'name': name,
                'description': strategy.__doc__ or '',
                'parameters': strategy.get_parameters(),
                'indicators': strategy.get_required_indicators()
            }
            for name, strategy in cls._strategies.items()
        ]
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize registry with all available strategies"""
        # Register all available strategies
        cls.register(SimpleMAStrategy)
        cls.register(RSIStrategy)
        cls.register(MACDStrategy)
        cls.register(CombinedStrategy)

# Initialize registry with all strategies
StrategyRegistry.initialize() 