from typing import Any, Dict, List, Optional, Union
from ..strategies.strategy_registry import StrategyRegistry

class ValidationService:
    """Service for handling parameter validation and default values"""
    
    INTERVALS = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
    DATA_SOURCES = ['yfinance', 'binance', 'coinbase']
    
    @staticmethod
    def validate_numeric_range(value: float, name: str, min_val: float, max_val: float, required: bool = True) -> float:
        """Validate a numeric value within a specified range"""
        if value is None:
            if required:
                raise ValueError(f"{name} is required")
            return None
            
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number")
            
        if value < min_val or value > max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}")
            
        return float(value)
    
    @staticmethod
    def validate_positive_number(value: float, name: str, required: bool = True) -> float:
        """Validate a positive number"""
        if value is None:
            if required:
                raise ValueError(f"{name} is required")
            return None
            
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number")
            
        if value <= 0:
            raise ValueError(f"{name} must be positive")
            
        return float(value)
    
    @staticmethod
    def validate_string_enum(value: str, name: str, valid_values: List[str], required: bool = True) -> str:
        """Validate a string against a list of valid values"""
        if value is None:
            if required:
                raise ValueError(f"{name} is required")
            return None
            
        if not isinstance(value, str):
            raise ValueError(f"{name} must be a string")
            
        if value not in valid_values:
            raise ValueError(f"{name} must be one of: {', '.join(valid_values)}")
            
        return value
    
    @classmethod
    def validate_backtest_params(cls, data: Dict[str, Any], app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare backtest parameters"""
        try:
            # Get strategy parameters
            strategy_params = data.get('strategy_params', {})
            
            # Prepare parameters with validation
            params = {
                'strategy_name': cls.validate_string_enum(
                    data.get('strategy'),
                    'Strategy',
                    StrategyRegistry.get_strategy_names()
                ),
                'period_days': cls.validate_positive_number(
                    data.get('period_days', app_config.get('DEFAULT_PERIOD_DAYS')),
                    'Period days'
                ),
                'interval': cls.validate_string_enum(
                    data.get('interval', app_config.get('DEFAULT_INTERVAL')),
                    'Interval',
                    cls.INTERVALS
                ),
                'initial_capital': cls.validate_positive_number(
                    data.get('initial_capital', app_config.get('DEFAULT_INITIAL_CAPITAL')),
                    'Initial capital'
                ),
                'stop_loss': cls.validate_numeric_range(
                    data.get('stop_loss', app_config.get('DEFAULT_STOP_LOSS')),
                    'Stop loss',
                    0, 1
                ),
                'take_profit': cls.validate_numeric_range(
                    data.get('take_profit', app_config.get('DEFAULT_TAKE_PROFIT')),
                    'Take profit',
                    0, 1
                ),
                'position_size': cls.validate_numeric_range(
                    data.get('position_size', app_config.get('DEFAULT_POSITION_SIZE')),
                    'Position size',
                    0, 1
                ),
                'commission': cls.validate_numeric_range(
                    data.get('commission', app_config.get('DEFAULT_COMMISSION')),
                    'Commission',
                    0, 1
                ),
                'strategy_params': strategy_params
            }
            
            return params
            
        except (ValueError, TypeError) as e:
            raise ValueError(f'Parameter validation error: {str(e)}')
    
    @classmethod
    def validate_settings(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare settings"""
        try:
            validated = {
                'defaultPeriodDays': cls.validate_positive_number(
                    data.get('defaultPeriodDays'),
                    'Default period days'
                ),
                'defaultInterval': cls.validate_string_enum(
                    data.get('defaultInterval'),
                    'Default interval',
                    cls.INTERVALS
                ),
                'defaultInitialCapital': cls.validate_positive_number(
                    data.get('defaultInitialCapital'),
                    'Default initial capital'
                ),
                'defaultStopLoss': cls.validate_numeric_range(
                    data.get('defaultStopLoss'),
                    'Default stop loss',
                    0, 1
                ),
                'defaultTakeProfit': cls.validate_numeric_range(
                    data.get('defaultTakeProfit'),
                    'Default take profit',
                    0, 1
                ),
                'defaultPositionSize': cls.validate_numeric_range(
                    data.get('defaultPositionSize'),
                    'Default position size',
                    0, 1
                ),
                'defaultCommission': cls.validate_numeric_range(
                    data.get('defaultCommission'),
                    'Default commission',
                    0, 1
                ),
                'dataSource': cls.validate_string_enum(
                    data.get('dataSource'),
                    'Data source',
                    cls.DATA_SOURCES
                ),
                'cacheTimeout': cls.validate_positive_number(
                    data.get('cacheTimeout'),
                    'Cache timeout'
                ),
                'maxBacktestPeriod': cls.validate_positive_number(
                    data.get('maxBacktestPeriod'),
                    'Max backtest period'
                ),
                'enableRealTimeData': bool(data.get('enableRealTimeData', False)),
                'enableNotifications': bool(data.get('enableNotifications', False)),
                'darkMode': bool(data.get('darkMode', False)),
                'apiKey': data.get('apiKey', ''),
                'apiSecret': data.get('apiSecret', '')
            }
            
            return validated
            
        except (ValueError, TypeError) as e:
            raise ValueError(f'Settings validation error: {str(e)}') 