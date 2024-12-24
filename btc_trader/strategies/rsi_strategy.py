from typing import Dict, Any, List
import pandas as pd
import numpy as np
from dataclasses import dataclass
from .base_strategy import BaseStrategy, StrategyParameters

@dataclass
class RSIParameters(StrategyParameters):
    """RSI strategy specific parameters"""
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70

class RSIStrategy(BaseStrategy):
    """RSI (Relative Strength Index) trading strategy
    
    This strategy generates trading signals based on RSI indicator:
    - Buy when RSI crosses below oversold level
    - Sell when RSI crosses above overbought level
    """
    
    def _initialize_parameters(self, **kwargs) -> RSIParameters:
        """Initialize RSI strategy parameters"""
        return RSIParameters(**kwargs)
    
    def _initialize_indicators(self) -> None:
        """Initialize RSI and other technical indicators"""
        # Calculate price changes
        delta = self._data['close'].diff()
        
        # Separate gains and losses
        gains = delta.copy()
        losses = delta.copy()
        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = abs(losses)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=self.parameters.rsi_period).mean()
        avg_losses = losses.rolling(window=self.parameters.rsi_period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses.replace(0, np.inf)
        self._data['rsi'] = 100 - (100 / (1 + rs))
    
    def _calculate_signal_strength(self, rsi_value: float) -> float:
        """Calculate signal strength based on RSI divergence"""
        if rsi_value <= self.parameters.rsi_oversold:
            return (self.parameters.rsi_oversold - rsi_value) / self.parameters.rsi_oversold
        elif rsi_value >= self.parameters.rsi_overbought:
            return (rsi_value - self.parameters.rsi_overbought) / (100 - self.parameters.rsi_overbought)
        return 0.0
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on RSI crossovers
        
        Returns:
            DataFrame with trading signals and RSI values
        """
        signals = self._data.copy()
        
        # Initialize signal columns
        signals['signal'] = 0
        signals['signal_strength'] = 0.0
        
        # Previous RSI values for crossover detection
        signals['prev_rsi'] = signals['rsi'].shift(1)
        
        # Generate buy signals - RSI crosses below oversold
        buy_signals = (signals['prev_rsi'] >= self.parameters.rsi_oversold) & \
                     (signals['rsi'] < self.parameters.rsi_oversold)
        signals.loc[buy_signals, 'signal'] = 1
        
        # Generate sell signals - RSI crosses above overbought
        sell_signals = (signals['prev_rsi'] <= self.parameters.rsi_overbought) & \
                      (signals['rsi'] > self.parameters.rsi_overbought)
        signals.loc[sell_signals, 'signal'] = -1
        
        # Calculate signal strength
        signals.loc[signals['signal'] != 0, 'signal_strength'] = \
            signals.loc[signals['signal'] != 0, 'rsi'].apply(self._calculate_signal_strength)
        
        # Clean up
        signals.drop('prev_rsi', axis=1, inplace=True)
        
        # Remove signals where RSI is not yet calculated
        signals.loc[signals['rsi'].isna(), ['signal', 'signal_strength']] = 0
        
        return signals
    
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
            'rsi_overbought': {
                'type': 'float',
                'default': 70,
                'min': 60,
                'max': 90,
                'description': 'RSI overbought threshold',
                'validate': lambda x, params: x > params.get('rsi_oversold', 0)
            },
            'rsi_oversold': {
                'type': 'float',
                'default': 30,
                'min': 10,
                'max': 40,
                'description': 'RSI oversold threshold',
                'validate': lambda x, params: x < params.get('rsi_overbought', 100)
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
        """Validate RSI strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate RSI-specific parameters
        if not 2 <= self.parameters.rsi_period <= 50:
            raise ValueError("RSI period must be between 2 and 50")
        if not 10 <= self.parameters.rsi_oversold <= 40:
            raise ValueError("RSI oversold threshold must be between 10 and 40")
        if not 60 <= self.parameters.rsi_overbought <= 90:
            raise ValueError("RSI overbought threshold must be between 60 and 90")
        if self.parameters.rsi_oversold >= self.parameters.rsi_overbought:
            raise ValueError("RSI oversold threshold must be less than overbought threshold")
            
        # Validate common parameters from base class
        return super().validate_parameters(**kwargs)