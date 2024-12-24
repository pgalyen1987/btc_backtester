import pandas as pd
import numpy as np
from typing import Dict, Any, List
from dataclasses import dataclass
from .base_strategy import BaseStrategy, StrategyParameters

@dataclass
class CombinedParameters(StrategyParameters):
    """Combined strategy specific parameters"""
    # Moving Average parameters
    ma_short: int = 20  # Within 5-50 range
    ma_long: int = 50   # Within 20-200 range
    
    # RSI parameters
    rsi_period: int = 14  # Within 2-50 range
    rsi_oversold: float = 30  # Within 10-40 range
    rsi_overbought: float = 70  # Within 60-90 range
    
    # MACD parameters
    macd_fast: int = 12  # Within 5-50 range
    macd_slow: int = 26  # Within 10-100 range
    macd_signal: int = 9  # Within 3-50 range

class CombinedStrategy(BaseStrategy):
    """Combined Strategy using multiple indicators
    
    This strategy combines signals from multiple indicators:
    - Moving Average Crossover
    - RSI for overbought/oversold conditions
    - MACD for trend confirmation
    
    Parameters:
        data (pd.DataFrame): Price data with OHLCV columns
        ma_short (int): Short MA period (default: 20, range: 5-50)
        ma_long (int): Long MA period (default: 50, range: 20-200)
        rsi_period (int): RSI period (default: 14, range: 2-50)
        rsi_oversold (float): RSI oversold threshold (default: 30, range: 10-40)
        rsi_overbought (float): RSI overbought threshold (default: 70, range: 60-90)
        macd_fast (int): MACD fast period (default: 12, range: 5-50)
        macd_slow (int): MACD slow period (default: 26, range: 10-100)
        macd_signal (int): MACD signal period (default: 9, range: 3-50)
        stop_loss (float): Stop loss percentage (default: 0.02, range: 0.1%-10%)
        take_profit (float): Take profit percentage (default: 0.03, range: 0.1%-20%)
        max_position_size (float): Maximum position size as a fraction of portfolio (default: 0.5, range: 10%-100%)
        commission (float): Trading commission percentage (default: 0.001, range: 0%-1%)
        use_volatility_filter (bool): Whether to use volatility filtering (default: False)
        volatility_window (int): Window size for volatility calculation (default: 20, range: 5-100)
        volatility_threshold (float): Threshold for volatility filter (default: 0.02, range: 0.1%-10%)
        trend_window (int): Window size for trend calculation (default: 50, range: 10-200)
        min_trend_strength (float): Minimum trend strength required for trading (default: 0.05, range: 1%-100%)
    """
    
    def _initialize_parameters(self, **kwargs) -> CombinedParameters:
        """Initialize strategy parameters"""
        return CombinedParameters(**kwargs)
    
    def __init__(self, data: pd.DataFrame, **kwargs):
        """Initialize strategy with data and indicator parameters"""
        super().__init__(data, **kwargs)
    
    @property
    def parameters(self) -> CombinedParameters:
        """Get strategy parameters with proper typing"""
        return self._parameters
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters with validation rules"""
        return {
            'ma_short': {
                'type': 'int',
                'default': 20,
                'min': 5,
                'max': 50,
                'description': 'Short-term moving average period',
                'validate': lambda x, params: x < params.get('ma_long', float('inf'))
            },
            'ma_long': {
                'type': 'int',
                'default': 50,
                'min': 20,
                'max': 200,
                'description': 'Long-term moving average period',
                'validate': lambda x, params: x > params.get('ma_short', 0)
            },
            'rsi_period': {
                'type': 'int',
                'default': 14,
                'min': 2,
                'max': 50,
                'description': 'RSI calculation period'
            },
            'rsi_oversold': {
                'type': 'float',
                'default': 30,
                'min': 10,
                'max': 40,
                'description': 'RSI oversold threshold',
                'validate': lambda x, params: x < params.get('rsi_overbought', 100)
            },
            'rsi_overbought': {
                'type': 'float',
                'default': 70,
                'min': 60,
                'max': 90,
                'description': 'RSI overbought threshold',
                'validate': lambda x, params: x > params.get('rsi_oversold', 0)
            },
            'macd_fast': {
                'type': 'int',
                'default': 12,
                'min': 5,
                'max': 50,
                'description': 'MACD fast period',
                'validate': lambda x, params: x < params.get('macd_slow', float('inf'))
            },
            'macd_slow': {
                'type': 'int',
                'default': 26,
                'min': 10,
                'max': 100,
                'description': 'MACD slow period',
                'validate': lambda x, params: x > params.get('macd_fast', 0)
            },
            'macd_signal': {
                'type': 'int',
                'default': 9,
                'min': 3,
                'max': 50,
                'description': 'MACD signal period'
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
        # Validate MA parameters
        if not 5 <= self.parameters.ma_short <= 50:
            raise ValueError("Short MA period must be between 5 and 50")
        if not 20 <= self.parameters.ma_long <= 200:
            raise ValueError("Long MA period must be between 20 and 200")
        if self.parameters.ma_short >= self.parameters.ma_long:
            raise ValueError("Short MA period must be less than long MA period")
            
        # Validate RSI parameters
        if not 2 <= self.parameters.rsi_period <= 50:
            raise ValueError("RSI period must be between 2 and 50")
        if not 10 <= self.parameters.rsi_oversold <= 40:
            raise ValueError("RSI oversold threshold must be between 10 and 40")
        if not 60 <= self.parameters.rsi_overbought <= 90:
            raise ValueError("RSI overbought threshold must be between 60 and 90")
        if self.parameters.rsi_oversold >= self.parameters.rsi_overbought:
            raise ValueError("RSI oversold threshold must be less than overbought threshold")
            
        # Validate MACD parameters
        if not 5 <= self.parameters.macd_fast <= 50:
            raise ValueError("MACD fast period must be between 5 and 50")
        if not 10 <= self.parameters.macd_slow <= 100:
            raise ValueError("MACD slow period must be between 10 and 100")
        if not 3 <= self.parameters.macd_signal <= 50:
            raise ValueError("MACD signal period must be between 3 and 50")
        if self.parameters.macd_fast >= self.parameters.macd_slow:
            raise ValueError("MACD fast period must be less than slow period")
            
        # Validate common parameters from base class
        return super().validate_parameters(**kwargs)
    
    @classmethod
    def get_required_indicators(cls) -> Dict[str, List[int]]:
        """Return required indicators with default parameters"""
        params = CombinedParameters()  # Use defaults from dataclass
        return {
            'SMA': [params.ma_short, params.ma_long],
            'RSI': [params.rsi_period],
            'MACD': [params.macd_fast, params.macd_slow, params.macd_signal]
        }
    
    def _calculate_signal_strength(self, signals: pd.DataFrame) -> float:
        """Calculate combined signal strength based on all indicators
        
        Returns:
            float: Signal strength between -1 and 1
            Positive values indicate bullish signals
            Negative values indicate bearish signals
            Magnitude indicates signal strength
        """
        # MA signal strength based on distance between averages
        ma_diff = signals['ma_short'] - signals['ma_long']
        ma_strength = ma_diff / signals['ma_long']  # Normalized difference
        
        # RSI signal strength
        rsi_value = signals['rsi'].iloc[-1]
        if rsi_value <= self.parameters.rsi_oversold:
            rsi_strength = (self.parameters.rsi_oversold - rsi_value) / self.parameters.rsi_oversold
        elif rsi_value >= self.parameters.rsi_overbought:
            rsi_strength = -(rsi_value - self.parameters.rsi_overbought) / (100 - self.parameters.rsi_overbought)
        else:
            rsi_strength = 0
        
        # MACD signal strength based on histogram
        macd_strength = signals['macd_hist'].iloc[-1] / signals['close'].iloc[-1]  # Normalize by price
        
        # Combine signals with equal weights
        total_strength = (ma_strength.iloc[-1] + rsi_strength + macd_strength) / 3
        
        # Clip to [-1, 1] range
        return np.clip(total_strength, -1, 1)
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on multiple indicators
        
        Returns:
            pd.DataFrame: DataFrame with signals and indicator values
        """
        signals = self.data.copy()
        
        # Calculate Moving Averages
        signals['ma_short'] = signals['close'].rolling(window=self.parameters.ma_short).mean()
        signals['ma_long'] = signals['close'].rolling(window=self.parameters.ma_long).mean()
        
        # Calculate RSI
        delta = signals['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.parameters.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.parameters.rsi_period).mean()
        # Handle division by zero in RSI calculation
        rs = gain / loss.replace(0, np.inf)
        signals['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = signals['close'].ewm(span=self.parameters.macd_fast, adjust=False).mean()
        exp2 = signals['close'].ewm(span=self.parameters.macd_slow, adjust=False).mean()
        signals['macd'] = exp1 - exp2
        signals['signal_line'] = signals['macd'].ewm(span=self.parameters.macd_signal, adjust=False).mean()
        signals['macd_hist'] = signals['macd'] - signals['signal_line']
        
        # Initialize signal column
        signals['signal'] = 0
        signals['signal_strength'] = 0.0
        
        # Previous values for crossover detection
        signals['prev_ma_diff'] = (signals['ma_short'] - signals['ma_long']).shift(1)
        signals['curr_ma_diff'] = signals['ma_short'] - signals['ma_long']
        signals['prev_macd_hist'] = signals['macd_hist'].shift(1)
        
        # Generate buy signals - Relaxed conditions using OR instead of AND
        ma_crossover_buy = (signals['curr_ma_diff'] > 0) & (signals['prev_ma_diff'] <= 0)
        rsi_oversold = signals['rsi'] < self.parameters.rsi_oversold
        macd_increasing = signals['macd_hist'] > signals['prev_macd_hist']
        
        # Buy if any two conditions are met
        buy_conditions = (
            (ma_crossover_buy & rsi_oversold) |
            (ma_crossover_buy & macd_increasing) |
            (rsi_oversold & macd_increasing)
        )
        signals.loc[buy_conditions, 'signal'] = 1
        
        # Generate sell signals - Relaxed conditions using OR instead of AND
        ma_crossover_sell = (signals['curr_ma_diff'] < 0) & (signals['prev_ma_diff'] >= 0)
        rsi_overbought = signals['rsi'] > self.parameters.rsi_overbought
        macd_decreasing = signals['macd_hist'] < signals['prev_macd_hist']
        
        # Sell if any two conditions are met
        sell_conditions = (
            (ma_crossover_sell & rsi_overbought) |
            (ma_crossover_sell & macd_decreasing) |
            (rsi_overbought & macd_decreasing)
        )
        signals.loc[sell_conditions, 'signal'] = -1
        
        # Calculate signal strength for each signal
        for i in range(len(signals)):
            if signals['signal'].iloc[i] != 0:
                strength = self._calculate_signal_strength(signals.iloc[:i+1])
                signals.loc[signals.index[i], 'signal_strength'] = strength
        
        # Clean up temporary columns
        signals.drop(['prev_ma_diff', 'curr_ma_diff', 'prev_macd_hist'], axis=1, inplace=True)
        
        # Remove signals where indicators are not yet calculated
        signals.loc[
            signals['ma_short'].isna() | 
            signals['ma_long'].isna() | 
            signals['rsi'].isna() | 
            signals['macd'].isna() | 
            signals['signal_line'].isna(),
            ['signal', 'signal_strength']
        ] = 0
        
        return signals
    
    def _initialize_indicators(self) -> None:
        """Initialize technical indicators used by the strategy"""
        signals = self.data.copy()
        
        # Calculate Moving Averages
        signals['ma_short'] = signals['close'].rolling(window=self.parameters.ma_short).mean()
        signals['ma_long'] = signals['close'].rolling(window=self.parameters.ma_long).mean()
        
        # Calculate RSI
        delta = signals['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.parameters.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.parameters.rsi_period).mean()
        rs = gain / loss.replace(0, np.inf)
        signals['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = signals['close'].ewm(span=self.parameters.macd_fast, adjust=False).mean()
        exp2 = signals['close'].ewm(span=self.parameters.macd_slow, adjust=False).mean()
        signals['macd'] = exp1 - exp2
        signals['signal_line'] = signals['macd'].ewm(span=self.parameters.macd_signal, adjust=False).mean()
        signals['macd_hist'] = signals['macd'] - signals['signal_line']
        
        # Store indicators
        self._indicators = signals[['ma_short', 'ma_long', 'rsi', 'macd', 'signal_line', 'macd_hist']]