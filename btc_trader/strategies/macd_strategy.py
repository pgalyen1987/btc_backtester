import pandas as pd
from typing import Dict, Any
from .base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    """MACD (Moving Average Convergence Divergence) Strategy
    
    This strategy generates trading signals based on MACD crossovers:
    - Buy when MACD line crosses above signal line
    - Sell when MACD line crosses below signal line
    Additional confirmation from histogram direction can be used
    
    Parameters:
        data (pd.DataFrame): Price data with OHLCV columns
        fast_period (int): Fast EMA period (default: 12)
        slow_period (int): Slow EMA period (default: 26)
        signal_period (int): Signal line period (default: 9)
        use_histogram (bool): Use histogram direction for confirmation (default: True)
    """
    
    def __init__(self, data: pd.DataFrame, fast_period: int = 12, 
                 slow_period: int = 26, signal_period: int = 9,
                 use_histogram: bool = True, **kwargs):
        """Initialize strategy with data and MACD parameters"""
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.use_histogram = use_histogram
        super().__init__(data, **kwargs)
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters with validation rules"""
        return {
            'fast_period': {
                'type': 'int',
                'default': 12,
                'min': 5,
                'max': 50,
                'description': 'Fast EMA period'
            },
            'slow_period': {
                'type': 'int',
                'default': 26,
                'min': 10,
                'max': 100,
                'description': 'Slow EMA period'
            },
            'signal_period': {
                'type': 'int',
                'default': 9,
                'min': 3,
                'max': 50,
                'description': 'Signal line period'
            },
            'use_histogram': {
                'type': 'bool',
                'default': True,
                'description': 'Use histogram direction for confirmation'
            }
        }
    
    @classmethod
    def get_required_indicators(cls) -> Dict[str, Any]:
        """Return required indicators with default parameters"""
        params = cls.get_parameters()
        return {
            'MACD': [
                params['fast_period']['default'],
                params['slow_period']['default'],
                params['signal_period']['default']
            ]
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        if not 5 <= self.fast_period <= 50:
            raise ValueError("Fast period must be between 5 and 50")
        if not 10 <= self.slow_period <= 100:
            raise ValueError("Slow period must be between 10 and 100")
        if not 3 <= self.signal_period <= 50:
            raise ValueError("Signal period must be between 3 and 50")
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")
        return True
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on MACD crossovers
        
        Returns:
            pd.DataFrame: DataFrame with signals and MACD values
        """
        signals = self.data.copy()
        
        # Calculate MACD components
        fast_ema = signals['Close'].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = signals['Close'].ewm(span=self.slow_period, adjust=False).mean()
        
        signals['MACD'] = fast_ema - slow_ema
        signals['Signal'] = signals['MACD'].ewm(span=self.signal_period, adjust=False).mean()
        signals['Histogram'] = signals['MACD'] - signals['Signal']
        
        # Initialize signal column
        signals['signal'] = 0
        
        # Previous values for crossover detection
        signals['prev_macd'] = signals['MACD'].shift(1)
        signals['prev_signal'] = signals['Signal'].shift(1)
        
        if self.use_histogram:
            # Use histogram direction for confirmation
            signals['hist_direction'] = signals['Histogram'].apply(lambda x: 1 if x > 0 else -1)
            signals['prev_hist_direction'] = signals['hist_direction'].shift(1)
            
            # Buy signal: MACD crosses above signal line with positive histogram
            signals.loc[
                (signals['MACD'] > signals['Signal']) & 
                (signals['prev_macd'] <= signals['prev_signal']) &
                (signals['hist_direction'] == 1),
                'signal'
            ] = 1
            
            # Sell signal: MACD crosses below signal line with negative histogram
            signals.loc[
                (signals['MACD'] < signals['Signal']) & 
                (signals['prev_macd'] >= signals['prev_signal']) &
                (signals['hist_direction'] == -1),
                'signal'
            ] = -1
            
            # Clean up histogram columns
            signals.drop(['hist_direction', 'prev_hist_direction'], axis=1, inplace=True)
        else:
            # Simple MACD crossover without histogram confirmation
            # Buy signal: MACD crosses above signal line
            signals.loc[
                (signals['MACD'] > signals['Signal']) & 
                (signals['prev_macd'] <= signals['prev_signal']),
                'signal'
            ] = 1
            
            # Sell signal: MACD crosses below signal line
            signals.loc[
                (signals['MACD'] < signals['Signal']) & 
                (signals['prev_macd'] >= signals['prev_signal']),
                'signal'
            ] = -1
        
        # Clean up temporary columns
        signals.drop(['prev_macd', 'prev_signal'], axis=1, inplace=True)
        
        # Remove signals where MACD components are not yet calculated
        signals.loc[signals['MACD'].isna() | signals['Signal'].isna(), 'signal'] = 0
        
        return signals