from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from .strategy_interface import (
    StrategyInterface, BacktestResult, BacktestMetrics, TradeResult
)

class BaseStrategy(StrategyInterface):
    """Base class for all trading strategies
    
    This class provides common functionality for all trading strategies:
    - Signal generation interface
    - Risk management
    - Backtesting
    - Parameter validation
    
    All strategies should inherit from this class and implement the required methods.
    """
    
    def __init__(self, data: pd.DataFrame, **kwargs):
        """Initialize strategy with data and parameters
        
        Args:
            data (pd.DataFrame): Price data with OHLCV columns
            **kwargs: Strategy-specific parameters
            
        Raises:
            ValueError: If data is invalid or missing required columns
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        if 'Close' not in data.columns:
            raise ValueError("Data must contain a 'Close' column")
            
        self.data = data
        self.positions = []
        self.current_position = None
        self.trade_log = []
        self.validate_parameters(**kwargs)
    
    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on the strategy
        
        Returns:
            pd.DataFrame: DataFrame with at least a 'signal' column containing:
                         1 for buy signals
                         -1 for sell signals
                         0 for no action
        """
        pass
    
    @classmethod
    def get_required_indicators(cls) -> Dict[str, Any]:
        """Default implementation returning empty dict
        
        Returns:
            Dict[str, Any]: Empty dictionary by default
        """
        return {}
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Return strategy information
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - name: Strategy class name
                - description: Strategy docstring
                - parameters: Strategy parameters
        """
        return {
            'name': self.__class__.__name__,
            'description': self.__class__.__doc__ or '',
            'parameters': self.__class__.get_parameters()
        }
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Return strategy parameters
        
        Returns:
            Dict[str, Any]: Empty dictionary by default
        """
        return {}
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate strategy parameters
        
        Args:
            **kwargs: Strategy-specific parameters
            
        Returns:
            bool: True if parameters are valid
            
        Raises:
            ValueError: If parameters are invalid
        """
        return True
    
    def apply_risk_management(self, signals: pd.DataFrame, stop_loss: float, take_profit: float) -> pd.DataFrame:
        """Apply risk management rules to the signals
        
        Args:
            signals (pd.DataFrame): DataFrame with trading signals
            stop_loss (float): Stop loss percentage as decimal (e.g., 0.02 for 2%)
            take_profit (float): Take profit percentage as decimal (e.g., 0.03 for 3%)
            
        Returns:
            pd.DataFrame: DataFrame with updated signals after risk management
            
        Raises:
            ValueError: If stop_loss or take_profit are invalid
        """
        if not 0 < stop_loss < 1:
            raise ValueError("Stop loss must be between 0 and 1")
        if not 0 < take_profit < 1:
            raise ValueError("Take profit must be between 0 and 1")
            
        signals = signals.copy()
        entry_price = None
        position = 0
        
        for i in range(len(signals)):
            if position == 0 and signals['signal'].iloc[i] == 1:  # New long position
                entry_price = signals['Close'].iloc[i]
                position = 1
            elif position == 1:
                current_price = signals['Close'].iloc[i]
                # Check stop loss
                if current_price < entry_price * (1 - stop_loss):
                    signals.loc[signals.index[i], 'signal'] = -1  # Force sell
                    position = 0
                # Check take profit
                elif current_price > entry_price * (1 + take_profit):
                    signals.loc[signals.index[i], 'signal'] = -1  # Take profit
                    position = 0
            
            if signals['signal'].iloc[i] == -1:
                position = 0
                entry_price = None
        
        return signals
    
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
            
        Raises:
            ValueError: If any parameters are invalid
        """
        if initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        if not 0 < position_size <= 1:
            raise ValueError("Position size must be between 0 and 1")
        if not 0 <= commission < 1:
            raise ValueError("Commission must be between 0 and 1")
            
        signals = self.generate_signals()
        signals = self.apply_risk_management(signals, stop_loss, take_profit)
        
        # Initialize portfolio
        portfolio = pd.DataFrame(index=signals.index)
        portfolio['positions'] = 0.0
        portfolio['cash'] = initial_capital
        portfolio['holdings'] = 0.0
        portfolio['total'] = initial_capital
        portfolio['returns'] = 0.0
        
        # Track positions and calculate returns
        position = 0
        entry_price = None
        entry_date = None
        trades: List[TradeResult] = []
        
        for i in range(len(signals)):
            if signals['signal'].iloc[i] == 1 and position == 0:  # Buy signal
                position = 1
                entry_price = signals['Close'].iloc[i]
                entry_date = signals.index[i]
                available_capital = portfolio['cash'].iloc[i] * position_size
                shares = (available_capital * (1 - commission)) / signals['Close'].iloc[i]
                portfolio.iloc[i:, portfolio.columns.get_loc('positions')] = shares
                portfolio.iloc[i:, portfolio.columns.get_loc('cash')] -= shares * signals['Close'].iloc[i] * (1 + commission)
                
                trades.append(TradeResult(
                    entry_date=str(entry_date),
                    exit_date=None,
                    entry_price=float(entry_price),
                    exit_price=0.0,
                    shares=float(shares),
                    return_value=0.0,
                    type='BUY'
                ))
                
            elif signals['signal'].iloc[i] == -1 and position == 1:  # Sell signal
                position = 0
                exit_price = signals['Close'].iloc[i]
                exit_date = signals.index[i]
                shares = portfolio['positions'].iloc[i]
                portfolio.iloc[i:, portfolio.columns.get_loc('positions')] = 0
                portfolio.iloc[i:, portfolio.columns.get_loc('cash')] += shares * signals['Close'].iloc[i] * (1 - commission)
                
                # Update last trade
                if trades:
                    trade_return = (exit_price - entry_price) / entry_price
                    trades[-1] = TradeResult(
                        entry_date=trades[-1].entry_date,
                        exit_date=str(exit_date),
                        entry_price=trades[-1].entry_price,
                        exit_price=float(exit_price),
                        shares=trades[-1].shares,
                        return_value=float(trade_return),
                        type=trades[-1].type
                    )
                
                entry_price = None
                entry_date = None
        
        # Close any open position at the end
        if position == 1:
            exit_price = signals['Close'].iloc[-1]
            exit_date = signals.index[-1]
            trade_return = (exit_price - entry_price) / entry_price if entry_price else 0.0
            if trades:
                trades[-1] = TradeResult(
                    entry_date=trades[-1].entry_date,
                    exit_date=str(exit_date),
                    entry_price=trades[-1].entry_price,
                    exit_price=float(exit_price),
                    shares=trades[-1].shares,
                    return_value=float(trade_return),
                    type=trades[-1].type
                )
        
        # Calculate holdings and total value
        portfolio['holdings'] = portfolio['positions'] * signals['Close']
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()
        
        # Calculate metrics
        returns = portfolio['returns'].dropna()
        winning_trades = [t for t in trades if t.return_value > 0]
        losing_trades = [t for t in trades if t.return_value <= 0]
        
        metrics = BacktestMetrics(
            total_return=(portfolio['total'].iloc[-1] - initial_capital) / initial_capital if not portfolio['total'].empty else 0.0,
            annual_return=returns.mean() * 252 if not returns.empty else 0.0,
            sharpe_ratio=(returns.mean() * 252) / (returns.std() * np.sqrt(252)) if not returns.empty and returns.std() != 0 else 0.0,
            sortino_ratio=(returns.mean() * 252) / (returns[returns < 0].std() * np.sqrt(252)) if len(returns[returns < 0]) > 0 else 0.0,
            max_drawdown=(portfolio['total'] / portfolio['total'].cummax() - 1).min() if not portfolio['total'].empty else 0.0,
            win_rate=len(winning_trades) / len(trades) if trades else 0.0,
            profit_factor=abs(sum(t.return_value for t in winning_trades) / sum(t.return_value for t in losing_trades)) if losing_trades else float('inf'),
            trade_count=len(trades),
            commission_paid=sum(t.shares * t.entry_price * commission + (t.shares * t.exit_price * commission if t.exit_price else 0) for t in trades)
        )
        
        return BacktestResult(
            metrics=metrics,
            portfolio=portfolio,
            trades=trades,
            signals=signals['signal'].fillna(0).astype(int).tolist()
        )