from .base_strategy import BaseStrategy, StrategyParameters
import pandas as pd
import numpy as np
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class SimpleMAParameters(StrategyParameters):
    """Simple MA strategy specific parameters"""
    short_window: int = 20  # Within 5-50 range
    long_window: int = 50   # Within 20-200 range

class SimpleMAStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy
    
    This strategy generates trading signals based on the crossover of two moving averages:
    - Buy when short-term MA crosses above long-term MA
    - Sell when short-term MA crosses below long-term MA
    """
    
    def _initialize_parameters(self, **kwargs) -> SimpleMAParameters:
        """Initialize strategy parameters"""
        return SimpleMAParameters(**kwargs)
    
    def _initialize_indicators(self) -> None:
        """Initialize technical indicators"""
        # Calculate moving averages
        self._data['ma_short'] = self._data['close'].rolling(window=self.parameters.short_window).mean()
        self._data['ma_long'] = self._data['close'].rolling(window=self.parameters.long_window).mean()
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on MA crossover
        
        Returns:
            pd.DataFrame: DataFrame with signals and moving averages
        """
        signals = self._data.copy()
        
        # Initialize signal column
        signals['signal'] = 0
        signals['signal_strength'] = 0.0
        
        # Generate crossover signals using vectorized operations
        signals['short_above'] = (signals['ma_short'] > signals['ma_long']).astype(int)
        signals['prev_short_above'] = signals['short_above'].shift(1)
        
        # Buy signal: Short MA crosses above Long MA
        buy_signals = (signals['short_above'] == 1) & (signals['prev_short_above'] == 0)
        signals.loc[buy_signals, 'signal'] = 1
        
        # Sell signal: Short MA crosses below Long MA
        sell_signals = (signals['short_above'] == 0) & (signals['prev_short_above'] == 1)
        signals.loc[sell_signals, 'signal'] = -1
        
        # Calculate signal strength based on MA difference
        ma_diff = (signals['ma_short'] - signals['ma_long']) / signals['ma_long']
        signals.loc[signals['signal'] != 0, 'signal_strength'] = ma_diff.abs()
        
        # Clean up temporary columns
        signals.drop(['short_above', 'prev_short_above'], axis=1, inplace=True)
        
        # Remove signals where moving averages are not yet calculated
        signals.loc[signals['ma_short'].isna() | signals['ma_long'].isna(), 'signal'] = 0
        
        return signals
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters with validation rules"""
        return {
            'short_window': {
                'type': 'int',
                'default': 20,
                'min': 5,
                'max': 50,
                'description': 'Short-term moving average period',
                'validate': lambda x, params: x < params.get('long_window', float('inf'))
            },
            'long_window': {
                'type': 'int',
                'default': 50,
                'min': 20,
                'max': 200,
                'description': 'Long-term moving average period',
                'validate': lambda x, params: x > params.get('short_window', 0)
            },
            'stop_loss': {
                'type': 'float',
                'default': 0.02,
                'min': 0.001,
                'max': 0.1,
                'description': 'Stop loss percentage'
            },
            'take_profit': {
                'type': 'float',
                'default': 0.03,
                'min': 0.001,
                'max': 0.2,
                'description': 'Take profit percentage'
            }
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate MA-specific parameters
        if not 5 <= self.parameters.short_window <= 50:
            raise ValueError("Short window must be between 5 and 50")
        if not 20 <= self.parameters.long_window <= 200:
            raise ValueError("Long window must be between 20 and 200")
        if self.parameters.short_window >= self.parameters.long_window:
            raise ValueError("Short window must be less than long window")
            
        # Validate common parameters from base class
        return super().validate_parameters(**kwargs)