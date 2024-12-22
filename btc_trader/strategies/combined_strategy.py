import pandas as pd
from typing import Dict, Any
from .base_strategy import BaseStrategy

class CombinedStrategy(BaseStrategy):
    """Combined Strategy using multiple indicators
    
    This strategy combines signals from multiple indicators:
    - Moving Average Crossover
    - RSI for overbought/oversold conditions
    - MACD for trend confirmation
    
    Parameters:
        data (pd.DataFrame): Price data with OHLCV columns
        ma_short (int): Short MA period (default: 20)
        ma_long (int): Long MA period (default: 50)
        rsi_period (int): RSI period (default: 14)
        rsi_threshold (int): RSI threshold (default: 30)
        macd_fast (int): MACD fast period (default: 12)
        macd_slow (int): MACD slow period (default: 26)
        macd_signal (int): MACD signal period (default: 9)
    """
    
    def __init__(self, data: pd.DataFrame, ma_short: int = 20, ma_long: int = 50,
                 rsi_period: int = 14, rsi_threshold: int = 30,
                 macd_fast: int = 12, macd_slow: int = 26, macd_signal: int = 9,
                 **kwargs):
        """Initialize strategy with data and indicator parameters"""
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.rsi_period = rsi_period
        self.rsi_threshold = rsi_threshold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        super().__init__(data, **kwargs)
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters with validation rules"""
        return {
            'ma_short': {
                'type': 'int',
                'default': 20,
                'min': 5,
                'max': 50,
                'description': 'Short-term moving average period'
            },
            'ma_long': {
                'type': 'int',
                'default': 50,
                'min': 20,
                'max': 200,
                'description': 'Long-term moving average period'
            },
            'rsi_period': {
                'type': 'int',
                'default': 14,
                'min': 2,
                'max': 50,
                'description': 'RSI calculation period'
            },
            'rsi_threshold': {
                'type': 'int',
                'default': 30,
                'min': 20,
                'max': 40,
                'description': 'RSI threshold for oversold/overbought'
            },
            'macd_fast': {
                'type': 'int',
                'default': 12,
                'min': 5,
                'max': 50,
                'description': 'MACD fast period'
            },
            'macd_slow': {
                'type': 'int',
                'default': 26,
                'min': 10,
                'max': 100,
                'description': 'MACD slow period'
            },
            'macd_signal': {
                'type': 'int',
                'default': 9,
                'min': 3,
                'max': 50,
                'description': 'MACD signal period'
            }
        }
    
    @classmethod
    def get_required_indicators(cls) -> Dict[str, Any]:
        """Return required indicators with default parameters"""
        params = cls.get_parameters()
        return {
            'SMA': [
                params['ma_short']['default'],
                params['ma_long']['default']
            ],
            'RSI': [params['rsi_period']['default']],
            'MACD': [
                params['macd_fast']['default'],
                params['macd_slow']['default'],
                params['macd_signal']['default']
            ]
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        if self.ma_short >= self.ma_long:
            raise ValueError("Short MA period must be less than long MA period")
        if not 5 <= self.ma_short <= 50:
            raise ValueError("Short MA period must be between 5 and 50")
        if not 20 <= self.ma_long <= 200:
            raise ValueError("Long MA period must be between 20 and 200")
        if not 2 <= self.rsi_period <= 50:
            raise ValueError("RSI period must be between 2 and 50")
        if not 20 <= self.rsi_threshold <= 40:
            raise ValueError("RSI threshold must be between 20 and 40")
        if self.macd_fast >= self.macd_slow:
            raise ValueError("MACD fast period must be less than slow period")
        return True
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on multiple indicators
        
        Returns:
            pd.DataFrame: DataFrame with signals and indicator values
        """
        signals = self.data.copy()
        
        # Calculate Moving Averages
        signals['MA_Short'] = signals['Close'].rolling(window=self.ma_short).mean()
        signals['MA_Long'] = signals['Close'].rolling(window=self.ma_long).mean()
        
        # Calculate RSI
        delta = signals['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        signals['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = signals['Close'].ewm(span=self.macd_fast, adjust=False).mean()
        exp2 = signals['Close'].ewm(span=self.macd_slow, adjust=False).mean()
        signals['MACD'] = exp1 - exp2
        signals['Signal_Line'] = signals['MACD'].ewm(span=self.macd_signal, adjust=False).mean()
        signals['MACD_Hist'] = signals['MACD'] - signals['Signal_Line']
        
        # Initialize signal column
        signals['signal'] = 0
        
        # Previous values for crossover detection
        signals['prev_ma_diff'] = (signals['MA_Short'] - signals['MA_Long']).shift(1)
        signals['curr_ma_diff'] = signals['MA_Short'] - signals['MA_Long']
        signals['prev_macd_hist'] = signals['MACD_Hist'].shift(1)
        
        # Generate buy signals
        buy_conditions = (
            # MA Crossover (short crosses above long)
            (signals['curr_ma_diff'] > 0) & 
            (signals['prev_ma_diff'] <= 0) &
            # RSI oversold
            (signals['RSI'] < self.rsi_threshold) &
            # MACD histogram increasing
            (signals['MACD_Hist'] > signals['prev_macd_hist'])
        )
        signals.loc[buy_conditions, 'signal'] = 1
        
        # Generate sell signals
        sell_conditions = (
            # MA Crossover (short crosses below long)
            (signals['curr_ma_diff'] < 0) & 
            (signals['prev_ma_diff'] >= 0) &
            # RSI overbought
            (signals['RSI'] > (100 - self.rsi_threshold)) &
            # MACD histogram decreasing
            (signals['MACD_Hist'] < signals['prev_macd_hist'])
        )
        signals.loc[sell_conditions, 'signal'] = -1
        
        # Clean up temporary columns
        signals.drop(['prev_ma_diff', 'curr_ma_diff', 'prev_macd_hist'], axis=1, inplace=True)
        
        # Remove signals where indicators are not yet calculated
        signals.loc[
            signals['MA_Short'].isna() | 
            signals['MA_Long'].isna() | 
            signals['RSI'].isna() | 
            signals['MACD'].isna() | 
            signals['Signal_Line'].isna(),
            'signal'
        ] = 0
        
        return signals