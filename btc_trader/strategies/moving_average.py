"""Moving Average Crossover Strategy"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from .base import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    """Strategy that generates signals based on moving average crossovers"""
    
    def validate_parameters(self) -> None:
        """Validate strategy parameters"""
        required_params = ['short_window', 'long_window']
        for param in required_params:
            if param not in self.parameters:
                raise ValueError(f"Missing required parameter: {param}")
            
            value = self.parameters[param]
            if not isinstance(value, (int, float)):
                raise ValueError(f"{param} must be a number")
            if value <= 0:
                raise ValueError(f"{param} must be greater than 0")
                
        if self.parameters['short_window'] >= self.parameters['long_window']:
            raise ValueError("Short window must be less than long window")
    
    def add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add moving averages to the data"""
        df = data.copy()
        
        # Calculate moving averages
        df['short_ma'] = df['close'].rolling(
            window=self.parameters['short_window']
        ).mean()
        df['long_ma'] = df['close'].rolling(
            window=self.parameters['long_window']
        ).mean()
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on moving average crossovers"""
        df = self.add_technical_indicators(data)
        
        # Initialize signal column
        df['signal'] = 0
        
        # Generate signals
        # Buy signal (1) when short MA crosses above long MA
        # Sell signal (-1) when short MA crosses below long MA
        df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
        df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1
        
        return df
    
    def calculate_position_size(self, data: pd.DataFrame, capital: float) -> pd.Series:
        """Calculate position size for each signal"""
        position_sizes = pd.Series(0.0, index=data.index)
        
        # Use fixed position size (can be enhanced with position sizing strategies)
        position_size = capital * 0.95  # Use 95% of capital
        position_sizes[data['signal'] != 0] = position_size
        
        return position_sizes
    
    def get_required_indicators(self) -> List[str]:
        """Get list of required technical indicators"""
        return ['SMA']
    
    def get_parameter_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about strategy parameters"""
        return {
            'short_window': {
                'type': 'int',
                'description': 'Period for short moving average',
                'default': 20,
                'min': 5,
                'max': 50,
                'required': True
            },
            'long_window': {
                'type': 'int',
                'description': 'Period for long moving average',
                'default': 50,
                'min': 20,
                'max': 200,
                'required': True
            }
        } 