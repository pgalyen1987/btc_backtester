"""RSI Strategy Implementation"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from .base import BaseStrategy

class RSIStrategy(BaseStrategy):
    """Strategy that generates signals based on RSI overbought/oversold levels"""
    
    def validate_parameters(self) -> None:
        """Validate strategy parameters"""
        required_params = ['period', 'overbought', 'oversold']
        for param in required_params:
            if param not in self.parameters:
                raise ValueError(f"Missing required parameter: {param}")
                
            value = self.parameters[param]
            if not isinstance(value, (int, float)):
                raise ValueError(f"{param} must be a number")
            elif param == 'period' and value <= 0:
                raise ValueError("Period must be greater than 0")
            elif param in ['overbought', 'oversold']:
                if not 0 <= value <= 100:
                    raise ValueError(f"{param} must be between 0 and 100")
                    
        if self.parameters['oversold'] >= self.parameters['overbought']:
            raise ValueError("Oversold level must be less than overbought level")
    
    def add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add RSI indicator to the data"""
        df = data.copy()
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(
            window=self.parameters['period']
        ).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(
            window=self.parameters['period']
        ).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on RSI levels"""
        df = self.add_technical_indicators(data)
        
        # Initialize signal column
        df['signal'] = 0
        
        # Generate signals
        # Buy signal (1) when RSI crosses below oversold level
        # Sell signal (-1) when RSI crosses above overbought level
        df.loc[df['rsi'] < self.parameters['oversold'], 'signal'] = 1
        df.loc[df['rsi'] > self.parameters['overbought'], 'signal'] = -1
        
        return df
    
    def calculate_position_size(self, data: pd.DataFrame, capital: float) -> pd.Series:
        """Calculate position size for each signal"""
        position_sizes = pd.Series(0.0, index=data.index)
        
        # Use dynamic position sizing based on RSI divergence
        df = self.add_technical_indicators(data)
        rsi_values = df['rsi']
        
        # Calculate position size based on RSI divergence from thresholds
        for idx in data[data['signal'] != 0].index:
            if data.loc[idx, 'signal'] == 1:  # Buy signal
                # More oversold = larger position
                divergence = (self.parameters['oversold'] - rsi_values[idx]) / self.parameters['oversold']
                size = capital * min(0.95, max(0.1, divergence))
                position_sizes[idx] = size
            else:  # Sell signal
                # More overbought = larger position
                divergence = (rsi_values[idx] - self.parameters['overbought']) / (100 - self.parameters['overbought'])
                size = capital * min(0.95, max(0.1, divergence))
                position_sizes[idx] = size
        
        return position_sizes
    
    def get_required_indicators(self) -> List[str]:
        """Get list of required technical indicators"""
        return ['RSI']
    
    def get_parameter_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about strategy parameters"""
        return {
            'period': {
                'type': 'int',
                'description': 'Period for RSI calculation',
                'default': 14,
                'min': 2,
                'max': 50,
                'required': True
            },
            'overbought': {
                'type': 'float',
                'description': 'RSI level considered overbought',
                'default': 70,
                'min': 50,
                'max': 90,
                'required': True
            },
            'oversold': {
                'type': 'float',
                'description': 'RSI level considered oversold',
                'default': 30,
                'min': 10,
                'max': 50,
                'required': True
            }
        } 