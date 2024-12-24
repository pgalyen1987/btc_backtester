from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from ..utils.validation import validate_backtest_params
from ..strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)

class Backtester:
    """Core backtesting engine that handles both historical and live data backtesting"""
    
    def __init__(self):
        self.data = None
        self.strategy = None
        self.portfolio = None
        self.performance = None
        
    def initialize(self, 
                  strategy: BaseStrategy,
                  initial_capital: float,
                  position_size: float,
                  stop_loss: float,
                  take_profit: float,
                  commission: float):
        """Initialize the backtesting engine with strategy and parameters"""
        self.strategy = strategy
        self.portfolio = {
            'cash': initial_capital,
            'position': 0,
            'total_value': initial_capital,
            'trades': [],
            'history': []
        }
        self.params = {
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'commission': commission
        }
        
    def load_data(self, data: pd.DataFrame):
        """Load price data for backtesting"""
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"Data must contain columns: {required_columns}")
            
        self.data = data.copy()
        self.data.set_index('timestamp', inplace=True)
        self.data.sort_index(inplace=True)
        
    def run(self) -> Dict[str, Any]:
        """Run the backtest"""
        if self.data is None:
            raise ValueError("No data loaded")
        if self.strategy is None:
            raise ValueError("No strategy initialized")
            
        signals = []
        portfolio_values = []
        trades = []
        
        # Initialize strategy
        self.strategy.initialize(self.data)
        
        # Iterate through each time step
        for i in range(len(self.data)):
            current_data = self.data.iloc[:i+1]
            current_price = current_data.iloc[-1]['close']
            
            # Get strategy signal
            signal = self.strategy.generate_signal(current_data)
            signals.append(signal)
            
            # Execute trades based on signal
            if signal != 0 and len(current_data) > 1:
                trade = self._execute_trade(signal, current_price)
                if trade:
                    trades.append(trade)
            
            # Update portfolio value
            self.portfolio['total_value'] = (
                self.portfolio['cash'] + 
                self.portfolio['position'] * current_price
            )
            portfolio_values.append(self.portfolio['total_value'])
            
            # Store portfolio history
            self.portfolio['history'].append({
                'timestamp': current_data.index[-1],
                'cash': self.portfolio['cash'],
                'position': self.portfolio['position'],
                'total_value': self.portfolio['total_value']
            })
            
        # Calculate performance metrics
        metrics = self._calculate_metrics(portfolio_values)
        
        return {
            'metrics': metrics,
            'signals': signals,
            'trades': trades,
            'portfolio': {
                'timestamps': [h['timestamp'] for h in self.portfolio['history']],
                'values': portfolio_values
            }
        }
        
    def _execute_trade(self, signal: int, price: float) -> Optional[Dict[str, Any]]:
        """Execute a trade based on the signal"""
        if signal == 0:
            return None
            
        position_value = self.portfolio['total_value'] * self.params['position_size']
        shares = position_value / price
        commission = position_value * self.params['commission']
        
        if signal > 0 and self.portfolio['position'] == 0:  # Buy
            if self.portfolio['cash'] >= position_value + commission:
                self.portfolio['cash'] -= position_value + commission
                self.portfolio['position'] = shares
                return {
                    'timestamp': self.data.index[-1],
                    'type': 'buy',
                    'price': price,
                    'shares': shares,
                    'value': position_value,
                    'commission': commission
                }
        elif signal < 0 and self.portfolio['position'] > 0:  # Sell
            position_value = self.portfolio['position'] * price
            commission = position_value * self.params['commission']
            self.portfolio['cash'] += position_value - commission
            self.portfolio['position'] = 0
            return {
                'timestamp': self.data.index[-1],
                'type': 'sell',
                'price': price,
                'shares': shares,
                'value': position_value,
                'commission': commission
            }
            
        return None
        
    def _calculate_metrics(self, portfolio_values: List[float]) -> Dict[str, float]:
        """Calculate performance metrics"""
        returns = pd.Series(portfolio_values).pct_change().dropna()
        
        total_return = (portfolio_values[-1] / portfolio_values[0]) - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if len(returns) > 1 else 0
        max_drawdown = self._calculate_max_drawdown(portfolio_values)
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.portfolio['trades']),
            'final_value': portfolio_values[-1]
        }
        
    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """Calculate maximum drawdown"""
        peak = portfolio_values[0]
        max_drawdown = 0
        
        for value in portfolio_values[1:]:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
            
        return max_drawdown 