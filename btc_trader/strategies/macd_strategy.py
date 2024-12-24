import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy
from ..utils.indicators import add_technical_indicators

class MACDStrategy(BaseStrategy):
    """MACD (Moving Average Convergence Divergence) Strategy
    
    This strategy generates trading signals based on MACD crossovers:
    - Buy when MACD line crosses above signal line with histogram confirmation
    - Sell when MACD line crosses below signal line with histogram confirmation
    - Additional filters for trend strength and volatility
    
    Parameters:
        data (pd.DataFrame): Price data with OHLCV columns
        fast_period (int): Fast EMA period (default: 12)
        slow_period (int): Slow EMA period (default: 26)
        signal_period (int): Signal line period (default: 9)
        min_trend_strength (float): Minimum trend strength threshold (default: 0.0002)
        use_volatility_filter (bool): Use volatility filter (default: True)
        volatility_window (int): Volatility calculation window (default: 20)
        volatility_threshold (float): Maximum allowed volatility (default: 0.05)
    """
    
    def __init__(self, data: pd.DataFrame, fast_period: int = 12, 
                 slow_period: int = 26, signal_period: int = 9,
                 min_trend_strength: float = 0.0002,
                 use_volatility_filter: bool = True,
                 volatility_window: int = 20,
                 volatility_threshold: float = 0.05,
                 **kwargs):
        """Initialize strategy with data and MACD parameters"""
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        kwargs.update({
            'min_trend_strength': min_trend_strength,
            'use_volatility_filter': use_volatility_filter,
            'volatility_window': volatility_window,
            'volatility_threshold': volatility_threshold
        })
        super().__init__(data, **kwargs)
    
    def validate_parameters(self, **kwargs) -> None:
        """Validate strategy parameters"""
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")
        if self.signal_period >= self.fast_period:
            raise ValueError("Signal period must be less than fast period")
    
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
                'max': 30,
                'description': 'Signal line period'
            },
            'min_trend_strength': {
                'type': 'float',
                'default': 0.05,
                'min': 0.01,
                'max': 1.0,
                'description': 'Minimum trend strength threshold'
            },
            'use_volatility_filter': {
                'type': 'bool',
                'default': True,
                'description': 'Use volatility filter'
            },
            'volatility_window': {
                'type': 'int',
                'default': 20,
                'min': 5,
                'max': 100,
                'description': 'Volatility calculation window'
            },
            'volatility_threshold': {
                'type': 'float',
                'default': 0.02,
                'min': 0.001,
                'max': 0.1,
                'description': 'Maximum allowed volatility'
            }
        }
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on MACD strategy
        
        Returns:
            pd.DataFrame: DataFrame with signals and confidence scores
        """
        # Add indicators
        df = add_technical_indicators(self.data, {
            'MACD': None,
            'BBANDS': None  # For volatility filter
        })
        
        # Initialize signals
        df['signal'] = 0
        df['confidence'] = 0.0
        
        # Generate signals
        for i in range(1, len(df)):
            # MACD crossover conditions
            macd_cross_up = df['MACD'].iloc[i-1] < df['MACD_SIGNAL'].iloc[i-1] and \
                          df['MACD'].iloc[i] > df['MACD_SIGNAL'].iloc[i]
            macd_cross_down = df['MACD'].iloc[i-1] > df['MACD_SIGNAL'].iloc[i-1] and \
                            df['MACD'].iloc[i] < df['MACD_SIGNAL'].iloc[i]
            
            # Check trend and volatility filters
            strong_trend, trend_strength, trend_direction = self.check_trend_filter(df['Close'], i)
            normal_volatility = self.check_volatility_filter(df, i)
            
            # Generate signals with confidence
            if macd_cross_up and trend_direction > 0 and strong_trend and normal_volatility:
                df.loc[df.index[i], 'signal'] = 1
                df.loc[df.index[i], 'confidence'] = self.calculate_confidence(trend_strength)
            elif macd_cross_down and trend_direction < 0 and strong_trend and normal_volatility:
                df.loc[df.index[i], 'signal'] = -1
                df.loc[df.index[i], 'confidence'] = self.calculate_confidence(trend_strength)
        
        return df