from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, ClassVar, TypeVar, Type
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class StrategyParameters:
    """Base class for strategy parameters"""
    stop_loss: float = 0.02  # 2% - within 0.1% to 10% range
    take_profit: float = 0.03  # 3% - within 0.1% to 20% range
    max_position_size: float = 0.5  # 50% - within 10% to 100% range
    commission: float = 0.001  # 0.1% - within 0% to 1% range
    use_volatility_filter: bool = False  # Default to simpler strategy
    volatility_window: int = 20  # Within 5 to 100 range
    volatility_threshold: float = 0.02  # 2% - within 0.1% to 10% range
    trend_window: int = 50  # Within 10 to 200 range
    min_trend_strength: float = 0.05  # 5% - within 1% to 100% range

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary"""
        return {
            key: getattr(self, key)
            for key in self.__dataclass_fields__
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyParameters':
        """Create parameters from dictionary"""
        return cls(**{
            key: data.get(key, field.default)
            for key, field in cls.__dataclass_fields__.items()
        })

@dataclass
class Position:
    """Represents an open trading position"""
    entry_date: datetime
    entry_price: float
    shares: float
    type: str
    stop_loss: float
    take_profit: float
    confidence: Optional[float] = None
    ml_features: Optional[Dict[str, float]] = None

@dataclass
class TradeResult:
    """Represents the result of a completed trade"""
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    shares: float
    return_value: float
    type: str
    confidence: Optional[float] = None
    ml_features: Optional[Dict[str, float]] = None

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
    avg_trade_duration: float
    avg_profit_per_trade: float
    max_consecutive_losses: int

    def to_dict(self) -> Dict[str, float]:
        """Convert metrics to dictionary"""
        return {
            key: getattr(self, key)
            for key in self.__dataclass_fields__
        }

class BaseStrategy(ABC):
    """Base class for all trading strategies
    
    This class provides common functionality for all trading strategies:
    - Signal generation interface
    - Risk management
    - Position sizing
    - Backtesting
    - Parameter validation
    - Common filters (volatility, trend)
    """
    
    def __init__(self, data: pd.DataFrame, **kwargs):
        """Initialize strategy with data and parameters"""
        self._validate_data(data)
        self._data = data.copy()
        self._positions: List[Position] = []
        self._current_position: Optional[Position] = None
        self._trade_log: List[TradeResult] = []
        self._parameters = self._initialize_parameters(**kwargs)
        self._initialize_indicators()
    
    @property
    def data(self) -> pd.DataFrame:
        """Get the strategy's data"""
        return self._data
    
    @property
    def positions(self) -> List[Position]:
        """Get current positions"""
        return self._positions.copy()
    
    @property
    def current_position(self) -> Optional[Position]:
        """Get current active position"""
        return self._current_position
    
    @property
    def trade_log(self) -> List[TradeResult]:
        """Get completed trades"""
        return self._trade_log.copy()
    
    @property
    def parameters(self) -> StrategyParameters:
        """Get strategy parameters"""
        return self._parameters
    
    @abstractmethod
    def generate_signals(self) -> pd.Series:
        """Generate trading signals based on the strategy
        
        Returns:
            Series of trading signals (1 for buy, -1 for sell, 0 for hold)
        """
        pass
    
    @abstractmethod
    def _initialize_parameters(self, **kwargs) -> StrategyParameters:
        """Initialize strategy-specific parameters"""
        pass
    
    @abstractmethod
    def _initialize_indicators(self) -> None:
        """Initialize technical indicators used by the strategy"""
        pass
    
    def _validate_data(self, data: pd.DataFrame) -> None:
        """Validate input data requirements"""
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be DatetimeIndex")
    
    def calculate_position_size(self, signal: int, price: float, portfolio_value: float) -> float:
        """Calculate the position size for a trade"""
        if signal == 0 or portfolio_value <= 0:
            return 0.0
        
        position_value = portfolio_value * self.parameters.max_position_size
        return position_value / price
    
    def apply_risk_management(self, position: Position, current_price: float) -> Optional[float]:
        """Apply risk management rules and return exit price if triggered"""
        if position.type == 'long':
            if current_price <= position.entry_price * (1 - position.stop_loss):
                return current_price  # Stop loss triggered
            if current_price >= position.entry_price * (1 + position.take_profit):
                return current_price  # Take profit triggered
        else:  # short position
            if current_price >= position.entry_price * (1 + position.stop_loss):
                return current_price  # Stop loss triggered
            if current_price <= position.entry_price * (1 - position.take_profit):
                return current_price  # Take profit triggered
        return None
    
    def _apply_volatility_filter(self, signals: pd.Series) -> pd.Series:
        """Apply volatility filter to signals"""
        if not self.parameters.use_volatility_filter:
            return signals
        
        volatility = self.data['close'].pct_change().rolling(
            window=self.parameters.volatility_window
        ).std()
        
        return signals.where(
            volatility <= self.parameters.volatility_threshold,
            0
        )
    
    def _apply_trend_filter(self, signals: pd.Series) -> pd.Series:
        """Apply trend filter to signals"""
        trend = self.data['close'].pct_change(
            periods=self.parameters.trend_window
        ).abs()
        
        return signals.where(
            trend >= self.parameters.min_trend_strength,
            0
        )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of the strategy"""
        return {
            'parameters': self.parameters.to_dict(),
            'positions': [vars(pos) for pos in self.positions],
            'current_position': vars(self.current_position) if self.current_position else None,
            'trade_log': [vars(trade) for trade in self.trade_log]
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set strategy state from saved state"""
        self._parameters = StrategyParameters.from_dict(state['parameters'])
        self._positions = [Position(**pos) for pos in state['positions']]
        self._current_position = Position(**state['current_position']) if state['current_position'] else None
        self._trade_log = [TradeResult(**trade) for trade in state['trade_log']]
    
    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Dict[str, Any]]:
        """Get parameter schema with validation rules"""
        return {
            'stop_loss': {
                'type': 'float',
                'default': 0.02,
                'min': 0.001,  # 0.1%
                'max': 0.1,    # 10%
                'description': 'Stop loss percentage'
            },
            'take_profit': {
                'type': 'float',
                'default': 0.03,
                'min': 0.001,  # 0.1%
                'max': 0.2,    # 20%
                'description': 'Take profit percentage'
            },
            'max_position_size': {
                'type': 'float',
                'default': 0.5,
                'min': 0.1,    # 10%
                'max': 1.0,    # 100%
                'description': 'Maximum position size as fraction of portfolio'
            },
            'commission': {
                'type': 'float',
                'default': 0.001,
                'min': 0.0,    # 0%
                'max': 0.01,   # 1%
                'description': 'Trading commission percentage'
            },
            'use_volatility_filter': {
                'type': 'bool',
                'default': False,
                'description': 'Whether to use volatility filter'
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
                'min': 0.001,  # 0.1%
                'max': 0.1,    # 10%
                'description': 'Maximum allowed volatility'
            },
            'trend_window': {
                'type': 'int',
                'default': 50,
                'min': 10,
                'max': 200,
                'description': 'Trend calculation window'
            },
            'min_trend_strength': {
                'type': 'float',
                'default': 0.05,
                'min': 0.01,   # 1%
                'max': 1.0,    # 100%
                'description': 'Minimum trend strength required'
            }
        }
    
    @classmethod
    def get_required_indicators(cls) -> Dict[str, List[int]]:
        """Get required technical indicators for the strategy"""
        return {
            'BBANDS': None  # Default Bollinger Bands for volatility filter
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate common strategy parameters
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate stop loss and take profit
        if not 0.001 <= self.parameters.stop_loss <= 0.1:
            raise ValueError("Stop loss must be between 0.1% and 10%")
        if not 0.001 <= self.parameters.take_profit <= 0.2:
            raise ValueError("Take profit must be between 0.1% and 20%")
            
        # Validate position sizing and commission
        if not 0.1 <= self.parameters.max_position_size <= 1.0:
            raise ValueError("Max position size must be between 0.1 and 1.0")
        if not 0.0 <= self.parameters.commission <= 0.01:
            raise ValueError("Commission must be between 0% and 1%")
            
        # Validate volatility filter parameters if enabled
        if self.parameters.use_volatility_filter:
            if not 5 <= self.parameters.volatility_window <= 100:
                raise ValueError("Volatility window must be between 5 and 100")
            if not 0.001 <= self.parameters.volatility_threshold <= 0.1:
                raise ValueError("Volatility threshold must be between 0.1% and 10%")
                
        # Validate trend parameters
        if not 10 <= self.parameters.trend_window <= 200:
            raise ValueError("Trend window must be between 10 and 200")
        if not 0.01 <= self.parameters.min_trend_strength <= 1.0:
            raise ValueError("Minimum trend strength must be between 0.01 and 1.0")
            
        return True