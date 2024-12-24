from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Type, TypeVar, Union
from dataclasses import dataclass
from datetime import datetime

T = TypeVar('T', bound='StrategyInterface')

@dataclass
class TradeResult:
    """Represents the result of a single trade"""
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: float
    shares: float
    return_value: float
    type: str
    confidence: Optional[float] = None
    ml_features: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with ISO format dates"""
        return {
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'shares': self.shares,
            'return_value': self.return_value,
            'type': self.type,
            'confidence': self.confidence,
            'ml_features': self.ml_features
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeResult':
        """Create from dictionary with ISO format dates"""
        return cls(
            entry_date=datetime.fromisoformat(data['entry_date']) if data.get('entry_date') else None,
            exit_date=datetime.fromisoformat(data['exit_date']) if data.get('exit_date') else None,
            entry_price=float(data['entry_price']),
            exit_price=float(data['exit_price']),
            shares=float(data['shares']),
            return_value=float(data['return_value']),
            type=str(data['type']),
            confidence=float(data['confidence']) if data.get('confidence') else None,
            ml_features=data.get('ml_features')
        )

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

@dataclass
class BacktestResult:
    """Contains all results from a backtest run"""
    metrics: BacktestMetrics
    portfolio: pd.DataFrame
    trades: List[TradeResult]
    signals: List[int]
    chart_paths: Optional[Dict[str, str]] = None
    model_metrics: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, float]] = None

class StrategyInterface(ABC):
    """Interface for all trading strategies (both traditional and ML-based)"""
    
    @abstractmethod
    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        """Initialize strategy with data and parameters"""
        pass
    
    @abstractmethod
    def generate_signals(self) -> pd.Series:
        """Generate trading signals based on the strategy
        
        Returns:
            Series of trading signals (1 for buy, -1 for sell, 0 for hold)
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> None:
        """Validate strategy parameters"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: int, price: float, portfolio_value: float) -> float:
        """Calculate the position size for a trade"""
        pass
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML strategies (optional for traditional strategies)"""
        return data
    
    def train(self, train_data: pd.DataFrame, validation_data: Optional[pd.DataFrame] = None) -> None:
        """Train ML model (optional for traditional strategies)"""
        pass
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Make predictions using ML model (optional for traditional strategies)"""
        return np.zeros(len(data))
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance from ML model (optional)"""
        return None
    
    def save_model(self, path: str) -> None:
        """Save ML model to disk (optional)"""
        pass
    
    def load_model(self, path: str) -> None:
        """Load ML model from disk (optional)"""
        pass
    
    @classmethod
    def from_config(cls: Type[T], config: Dict[str, Any]) -> T:
        """Create strategy instance from configuration dictionary"""
        return cls(**config)
    
    def get_required_data_columns(self) -> List[str]:
        """Get list of required data columns for the strategy"""
        return ['Open', 'High', 'Low', 'Close', 'Volume']
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and current parameters"""
        return {
            'name': self.__class__.__name__,
            'type': 'ML' if hasattr(self, 'model') else 'Traditional',
            'parameters': self.__dict__
        }