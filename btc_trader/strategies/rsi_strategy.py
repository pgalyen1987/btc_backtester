import pandas as pd
from typing import Dict, Any
from .base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    """RSI (Relative Strength Index) Strategy
    
    This strategy generates trading signals based on RSI values:
    - Buy when RSI crosses below oversold level
    - Sell when RSI crosses above overbought level
    
    Parameters:
        data (pd.DataFrame): Price data with OHLCV columns
        rsi_period (int): RSI calculation period (default: 14)
        oversold (float): Oversold threshold (default: 30)
        overbought (float): Overbought threshold (default: 70)
    """
    
    def __init__(self, data: pd.DataFrame, rsi_period: int = 14, 
                 oversold: float = 30, overbought: float = 70, **kwargs):
        """Initialize strategy with data and RSI parameters"""
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        super().__init__(data, **kwargs)
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters with validation rules"""
        return {
            'rsi_period': {
                'type': 'int',
                'default': 14,
                'min': 2,
                'max': 50,
                'description': 'RSI calculation period'
            },
            'oversold': {
                'type': 'float',
                'default': 30,
                'min': 10,
                'max': 40,
                'description': 'Oversold threshold'
            },
            'overbought': {
                'type': 'float',
                'default': 70,
                'min': 60,
                'max': 90,
                'description': 'Overbought threshold'
            }
        }
    
    @classmethod
    def get_required_indicators(cls) -> Dict[str, Any]:
        """Return required indicators with default parameters"""
        params = cls.get_parameters()
        return {
            'RSI': [params['rsi_period']['default']]
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        if not 2 <= self.rsi_period <= 50:
            raise ValueError("RSI period must be between 2 and 50")
        if not 10 <= self.oversold <= 40:
            raise ValueError("Oversold threshold must be between 10 and 40")
        if not 60 <= self.overbought <= 90:
            raise ValueError("Overbought threshold must be between 60 and 90")
        if self.oversold >= self.overbought:
            raise ValueError("Oversold threshold must be less than overbought threshold")
        return True
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on RSI values
        
        Returns:
            pd.DataFrame: DataFrame with signals and RSI values
        """
        signals = self.data.copy()
        
        # Calculate RSI
        delta = signals['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        signals[f'RSI_{self.rsi_period}'] = 100 - (100 / (1 + rs))
        
        # Initialize signal column
        signals['signal'] = 0
        
        # Previous RSI values for crossover detection
        signals['prev_rsi'] = signals[f'RSI_{self.rsi_period}'].shift(1)
        
        # Buy signal: RSI crosses below oversold
        signals.loc[
            (signals[f'RSI_{self.rsi_period}'] <= self.oversold) & 
            (signals['prev_rsi'] > self.oversold),
            'signal'
        ] = 1
        
        # Sell signal: RSI crosses above overbought
        signals.loc[
            (signals[f'RSI_{self.rsi_period}'] >= self.overbought) & 
            (signals['prev_rsi'] < self.overbought),
            'signal'
        ] = -1
        
        # Clean up temporary columns
        signals.drop(['prev_rsi'], axis=1, inplace=True)
        
        # Remove signals where RSI is not yet calculated
        signals.loc[signals[f'RSI_{self.rsi_period}'].isna(), 'signal'] = 0
        
        return signals