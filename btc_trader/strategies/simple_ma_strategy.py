from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict, Any

class SimpleMAStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy
    
    This strategy generates trading signals based on the crossover of two moving averages:
    - Buy when short-term MA crosses above long-term MA
    - Sell when short-term MA crosses below long-term MA
    
    Parameters:
        data (pd.DataFrame): Price data with OHLCV columns
        short_window (int): Short-term moving average window (default: 20)
        long_window (int): Long-term moving average window (default: 50)
    """
    
    def __init__(self, data: pd.DataFrame, short_window: int = 20, long_window: int = 50, **kwargs):
        """Initialize strategy with data and MA parameters"""
        if not isinstance(data, pd.DataFrame) or 'Close' not in data.columns:
            raise ValueError("Data must be a DataFrame with a 'Close' column")
        
        self.short_window = short_window
        self.long_window = long_window
        super().__init__(data, **kwargs)
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters with validation rules"""
        return {
            'short_window': {
                'type': 'int',
                'default': 20,
                'min': 5,
                'max': 100,
                'description': 'Short-term moving average window'
            },
            'long_window': {
                'type': 'int',
                'default': 50,
                'min': 10,
                'max': 200,
                'description': 'Long-term moving average window'
            }
        }
    
    @classmethod
    def get_required_indicators(cls) -> Dict[str, Any]:
        """Return required indicators with default parameters"""
        params = cls.get_parameters()
        return {
            'SMA': [
                params['short_window']['default'],
                params['long_window']['default']
            ]
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        if self.short_window >= self.long_window:
            raise ValueError("Short window must be less than long window")
        if self.short_window < self.get_parameters()['short_window']['min']:
            raise ValueError(f"Short window must be at least {self.get_parameters()['short_window']['min']}")
        if self.long_window > self.get_parameters()['long_window']['max']:
            raise ValueError(f"Long window must be less than {self.get_parameters()['long_window']['max']}")
        return True
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on MA crossover
        
        Returns:
            pd.DataFrame: DataFrame with signals and moving averages
        """
        signals = self.data.copy()
        
        # Calculate moving averages using numpy for efficiency
        close_array = signals['Close'].values
        short_ma = pd.Series(
            np.concatenate([
                np.full(self.short_window - 1, np.nan),
                np.convolve(close_array, np.ones(self.short_window)/self.short_window, mode='valid')
            ]),
            index=signals.index
        )
        long_ma = pd.Series(
            np.concatenate([
                np.full(self.long_window - 1, np.nan),
                np.convolve(close_array, np.ones(self.long_window)/self.long_window, mode='valid')
            ]),
            index=signals.index
        )
        
        # Store MAs for visualization
        signals['short_ma'] = short_ma
        signals['long_ma'] = long_ma
        
        # Initialize signal column
        signals['signal'] = 0
        
        # Generate crossover signals using vectorized operations
        signals['short_above'] = (short_ma > long_ma).astype(int)
        signals['prev_short_above'] = signals['short_above'].shift(1)
        
        # Buy signal: Short MA crosses above Long MA
        signals.loc[
            (signals['short_above'] == 1) & 
            (signals['prev_short_above'] == 0),
            'signal'
        ] = 1
        
        # Sell signal: Short MA crosses below Long MA
        signals.loc[
            (signals['short_above'] == 0) & 
            (signals['prev_short_above'] == 1),
            'signal'
        ] = -1
        
        # Clean up temporary columns
        signals.drop(['short_above', 'prev_short_above'], axis=1, inplace=True)
        
        # Remove signals where moving averages are not yet calculated
        signals.loc[signals['short_ma'].isna() | signals['long_ma'].isna(), 'signal'] = 0
        
        return signals