from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Any, Optional, Type, TypeVar
from dataclasses import dataclass

T = TypeVar('T', bound='StrategyInterface')

@dataclass
class TradeResult:
    """Represents the result of a single trade"""
    entry_date: str
    exit_date: Optional[str]
    entry_price: float
    exit_price: float
    shares: float
    return_value: float
    type: str

@dataclass
class BacktestMetrics:
    """Contains metrics from a backtest run"""
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    trade_count: int
    commission_paid: float

@dataclass
class BacktestResult:
    """Contains all results from a backtest run"""
    metrics: BacktestMetrics
    portfolio: pd.DataFrame
    trades: List[TradeResult]
    signals: List[int]

class StrategyInterface(ABC):
    """Interface for all trading strategies"""
    
    @abstractmethod
    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        """Initialize strategy with data and parameters"""
        pass
    
    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals
        
        Returns:
            pd.DataFrame: DataFrame with at least 'signal' column containing values:
                         1 for buy signals, -1 for sell signals, 0 for no action
        """
        pass
    
    def apply_risk_management(self, signals: pd.DataFrame, stop_loss: float, take_profit: float) -> pd.DataFrame:
        """Apply risk management rules to the signals
        
        Args:
            signals (pd.DataFrame): DataFrame with trading signals
            stop_loss (float): Stop loss percentage as decimal (e.g., 0.02 for 2%)
            take_profit (float): Take profit percentage as decimal (e.g., 0.03 for 3%)
            
        Returns:
            pd.DataFrame: DataFrame with updated signals after risk management
        """
        pass
    
    def backtest(self, initial_capital: float, stop_loss: float, 
                take_profit: float, position_size: float, 
                commission: float) -> BacktestResult:
        """Run backtest with specified parameters
        
        Args:
            initial_capital (float): Starting capital for the backtest
            stop_loss (float): Stop loss percentage as decimal
            take_profit (float): Take profit percentage as decimal
            position_size (float): Position size as percentage of capital
            commission (float): Commission percentage per trade
            
        Returns:
            BacktestResult: Complete results of the backtest
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_required_indicators(cls) -> Dict[str, Any]:
        """Return dictionary of required indicators and their parameters
        
        Returns:
            Dict[str, Any]: Dictionary mapping indicator names to their parameters
        """
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """Return strategy information including name, description, and parameters
        
        Returns:
            Dict[str, Any]: Strategy information dictionary
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters
        
        Returns:
            Dict[str, Any]: Dictionary of parameter specifications
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """Validate strategy parameters
        
        Args:
            **kwargs: Strategy parameters to validate
            
        Returns:
            bool: True if parameters are valid
            
        Raises:
            ValueError: If parameters are invalid
        """
        pass