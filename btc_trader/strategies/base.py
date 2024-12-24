"""Base strategy class for BTC Trader"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, parameters: Dict[str, Any]):
        """Initialize strategy
        
        Args:
            parameters: Strategy parameters
        """
        self.parameters = parameters
        self.validate_parameters()
        
    @abstractmethod
    def validate_parameters(self) -> None:
        """Validate strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        pass
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals
        
        Args:
            data: DataFrame with market data
            
        Returns:
            DataFrame with added signal column
        """
        pass
        
    @abstractmethod
    def calculate_position_size(self, data: pd.DataFrame, capital: float) -> pd.Series:
        """Calculate position size for each signal
        
        Args:
            data: DataFrame with market data and signals
            capital: Available capital
            
        Returns:
            Series with position sizes
        """
        pass
        
    def add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators used by the strategy
        
        Args:
            data: DataFrame with market data
            
        Returns:
            DataFrame with added indicators
        """
        return data
        
    def get_required_indicators(self) -> List[str]:
        """Get list of required technical indicators
        
        Returns:
            List of indicator names
        """
        return []
        
    def get_parameter_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about strategy parameters
        
        Returns:
            Dictionary with parameter information
        """
        return {}
        
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information
        
        Returns:
            Dictionary with strategy information
        """
        return {
            'name': self.__class__.__name__,
            'description': self.__doc__ or '',
            'parameters': self.get_parameter_info(),
            'indicators': self.get_required_indicators()
        } 