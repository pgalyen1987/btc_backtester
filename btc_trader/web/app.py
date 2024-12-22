from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import json

from ..services.backtest_service import BacktestService
from ..strategies.strategy_registry import StrategyRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
backtest_service = BacktestService()

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get list of available strategies with their parameters"""
    try:
        strategies = backtest_service.get_available_strategies()
        return jsonify({'strategies': strategies})
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest with specified parameters"""
    try:
        data = request.get_json()
        
        # Extract parameters
        strategy_name = data.get('strategy')
        period_days = int(data.get('period_days', 365))
        interval = data.get('interval', '1d')
        initial_capital = float(data.get('initial_capital', 10000.0))
        stop_loss = float(data.get('stop_loss', 0.02))
        take_profit = float(data.get('take_profit', 0.03))
        position_size = float(data.get('position_size', 1.0))
        commission = float(data.get('commission', 0.001))
        strategy_params = data.get('strategy_params', {})
        
        # Validate required parameters
        if not strategy_name:
            return jsonify({'error': 'Strategy name is required'}), 400
            
        # Run backtest
        result = backtest_service.run_backtest(
            strategy_name=strategy_name,
            period_days=period_days,
            interval=interval,
            initial_capital=initial_capital,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            commission=commission,
            strategy_params=strategy_params
        )
        
        # Convert DataFrame to list for JSON serialization
        portfolio_data = {
            'dates': [str(date) for date in result.portfolio.index],
            'total': [float(x) if pd.notna(x) and not np.isinf(x) else 0.0 for x in result.portfolio['total'].tolist()],
            'returns': [float(x) if pd.notna(x) and not np.isinf(x) else 0.0 for x in result.portfolio['returns'].tolist()]
        }
        
        # Prepare response
        response = {
            'metrics': {
                'total_return': float(result.metrics.total_return) if not np.isinf(result.metrics.total_return) else 0.0,
                'annual_return': float(result.metrics.annual_return) if not np.isinf(result.metrics.annual_return) else 0.0,
                'sharpe_ratio': float(result.metrics.sharpe_ratio) if not np.isinf(result.metrics.sharpe_ratio) else 0.0,
                'sortino_ratio': float(result.metrics.sortino_ratio) if not np.isinf(result.metrics.sortino_ratio) else 0.0,
                'max_drawdown': float(result.metrics.max_drawdown) if not np.isinf(result.metrics.max_drawdown) else 0.0,
                'win_rate': float(result.metrics.win_rate) if not np.isinf(result.metrics.win_rate) else 0.0,
                'profit_factor': float(result.metrics.profit_factor) if not np.isinf(result.metrics.profit_factor) else 0.0,
                'trade_count': int(result.metrics.trade_count),
                'commission_paid': float(result.metrics.commission_paid) if not np.isinf(result.metrics.commission_paid) else 0.0
            },
            'portfolio': portfolio_data,
            'trades': [
                {
                    'entry_date': str(trade.entry_date),
                    'exit_date': str(trade.exit_date) if trade.exit_date else None,
                    'entry_price': float(trade.entry_price) if not np.isinf(trade.entry_price) else 0.0,
                    'exit_price': float(trade.exit_price) if not np.isinf(trade.exit_price) else 0.0,
                    'shares': float(trade.shares) if not np.isinf(trade.shares) else 0.0,
                    'return': float(trade.return_value) if not np.isinf(trade.return_value) else 0.0,
                    'type': str(trade.type)
                }
                for trade in result.trades
            ],
            'signals': [int(x) if pd.notna(x) and not np.isinf(x) else 0 for x in result.signals]
        }
        
        return jsonify(response)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/parameters', methods=['GET'])
def get_strategy_parameters():
    """Get parameters for a specific strategy"""
    try:
        strategy_name = request.args.get('strategy')
        if not strategy_name:
            return jsonify({'error': 'Strategy name is required'}), 400
            
        parameters = backtest_service.get_strategy_parameters(strategy_name)
        return jsonify({'parameters': parameters})
    except Exception as e:
        logger.error(f"Error getting strategy parameters: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 