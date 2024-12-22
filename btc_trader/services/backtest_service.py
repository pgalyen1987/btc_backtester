from typing import Dict, Any, Optional, List
import pandas as pd
import logging
from datetime import datetime, timedelta
import hashlib
import json

from ..data.data_loader import DataLoader
from ..utils.indicators import add_technical_indicators
from ..strategies.strategy_registry import StrategyRegistry
from ..strategies.strategy_interface import BacktestResult

logger = logging.getLogger(__name__)

class BacktestService:
    """Service for handling backtesting operations"""
    
    def __init__(self, default_symbol: str = "BTC-USD", cache_size: int = 10):
        """Initialize backtest service
        
        Args:
            default_symbol: Default trading symbol
            cache_size: Maximum number of datasets to cache
        """
        self.default_symbol = default_symbol
        self.cache_size = cache_size
        self.data_loader = DataLoader()
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.results_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_cache_key(self, symbol: str, period_days: int, interval: str) -> str:
        """Generate a unique cache key for the dataset
        
        Args:
            symbol: Trading symbol
            period_days: Number of days of data
            interval: Data interval
            
        Returns:
            Unique cache key string
        """
        params = f"{symbol}_{period_days}_{interval}"
        return hashlib.md5(params.encode()).hexdigest()
    
    def _manage_cache(self) -> None:
        """Remove oldest entries if cache exceeds size limit"""
        if len(self.data_cache) > self.cache_size:
            # Remove oldest entries based on last access time
            sorted_keys = sorted(
                self.data_cache.keys(),
                key=lambda k: self.data_cache[k].get('last_access', datetime.min)
            )
            for key in sorted_keys[:-self.cache_size]:
                del self.data_cache[key]
    
    def _prepare_data(self, 
                     period_days: int, 
                     interval: str, 
                     symbol: Optional[str] = None) -> pd.DataFrame:
        """Prepare data with indicators for backtesting
        
        Args:
            period_days: Number of days of historical data to fetch
            interval: Data interval (e.g., '1d', '1h')
            symbol: Optional trading symbol (uses default if not provided)
            
        Returns:
            DataFrame with price data and indicators
            
        Raises:
            ValueError: If no data is received or parameters are invalid
        """
        if period_days <= 0:
            raise ValueError("Period days must be positive")
        if not interval:
            raise ValueError("Interval must be specified")
            
        symbol = symbol or self.default_symbol
        cache_key = self._get_cache_key(symbol, period_days, interval)
        
        # Check cache
        if cache_key in self.data_cache:
            cached_data = self.data_cache[cache_key]
            cached_data['last_access'] = datetime.now()
            return cached_data['data']
        
        try:
            # Fetch data
            data = self.data_loader.fetch_data(
                symbol=symbol,
                period_days=period_days,
                interval=interval
            )
            
            if data.empty:
                raise ValueError(f"No data received for {symbol}")
            
            # Get all required indicators from registered strategies
            indicators = {}
            for strategy_info in StrategyRegistry.get_all_strategies():
                try:
                    strategy_class = StrategyRegistry.get_strategy(strategy_info['name'])
                    if strategy_class:
                        strategy_indicators = strategy_class.get_required_indicators()
                        indicators.update(strategy_indicators)
                except Exception as e:
                    logger.warning(f"Error getting indicators for strategy {strategy_info['name']}: {e}")
            
            # Add indicators
            try:
                data_with_indicators = add_technical_indicators(data, indicators)
            except Exception as e:
                logger.error(f"Error adding indicators: {e}")
                raise ValueError(f"Failed to add indicators: {e}")
            
            # Update cache
            self.data_cache[cache_key] = {
                'data': data_with_indicators,
                'last_access': datetime.now()
            }
            self._manage_cache()
            
            return data_with_indicators
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise ValueError(f"Failed to prepare data: {e}")
    
    def run_backtest(self, 
                    strategy_name: str,
                    period_days: int = 365,
                    interval: str = '1d',
                    initial_capital: float = 10000.0,
                    stop_loss: float = 0.02,
                    take_profit: float = 0.03,
                    position_size: float = 1.0,
                    commission: float = 0.001,
                    symbol: Optional[str] = None,
                    strategy_params: Optional[Dict[str, Any]] = None) -> BacktestResult:
        """Run a backtest with specified parameters
        
        Args:
            strategy_name: Name of strategy to use
            period_days: Number of days of historical data
            interval: Data interval (e.g., '1d', '1h')
            initial_capital: Starting capital for backtest
            stop_loss: Stop loss percentage as decimal
            take_profit: Take profit percentage as decimal
            position_size: Position size as percentage of capital
            commission: Commission percentage per trade
            symbol: Optional trading symbol (uses default if not provided)
            strategy_params: Optional strategy-specific parameters
            
        Returns:
            BacktestResult containing metrics, portfolio, trades, and signals
            
        Raises:
            ValueError: If strategy not found or parameters invalid
        """
        try:
            # Validate parameters
            if initial_capital <= 0:
                raise ValueError("Initial capital must be positive")
            if not 0 <= stop_loss < 1:
                raise ValueError("Stop loss must be between 0 and 1")
            if not 0 <= take_profit < 1:
                raise ValueError("Take profit must be between 0 and 1")
            if not 0 < position_size <= 1:
                raise ValueError("Position size must be between 0 and 1")
            if not 0 <= commission < 1:
                raise ValueError("Commission must be between 0 and 1")
            
            # Prepare data
            data = self._prepare_data(period_days, interval, symbol)
            
            # Create strategy instance
            strategy_class = StrategyRegistry.get_strategy(strategy_name)
            if not strategy_class:
                raise ValueError(f"Strategy '{strategy_name}' not found")
                
            strategy_params = strategy_params or {}
            try:
                strategy = strategy_class(data, **strategy_params)
            except Exception as e:
                raise ValueError(f"Failed to create strategy: {e}")
            
            # Run backtest
            try:
                result = strategy.backtest(
                    initial_capital=initial_capital,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=position_size,
                    commission=commission
                )
            except Exception as e:
                raise ValueError(f"Backtest failed: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in run_backtest: {e}")
            raise
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """Get information about all available strategies
        
        Returns:
            List of dictionaries containing strategy information
            
        Raises:
            RuntimeError: If no strategies are registered
        """
        strategies = StrategyRegistry.get_all_strategies()
        if not strategies:
            raise RuntimeError("No strategies are registered")
        return strategies
    
    def get_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Get parameters for a specific strategy
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dictionary of parameter specifications
            
        Raises:
            ValueError: If strategy not found
        """
        strategy_class = StrategyRegistry.get_strategy(strategy_name)
        if not strategy_class:
            raise ValueError(f"Strategy '{strategy_name}' not found")
        return strategy_class.get_parameters()