"""Validation utilities for BTC Trader"""

from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from datetime import datetime

def validate_data(data: pd.DataFrame) -> Tuple[bool, str]:
    """Validate input data
    
    Args:
        data: DataFrame containing market data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if data is None or len(data) == 0:
        return False, "No data provided"
        
    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
        
    # Check for missing values
    if data[required_columns].isna().any().any():
        return False, "Data contains missing values"
        
    # Check for invalid values
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_columns:
        if (data[col] <= 0).any():
            return False, f"Invalid values (<=0) in column: {col}"
            
    # Check price consistency
    invalid_prices = (
        (data['low'] > data['high']) |
        (data['open'] > data['high']) |
        (data['open'] < data['low']) |
        (data['close'] > data['high']) |
        (data['close'] < data['low'])
    )
    if invalid_prices.any():
        return False, "Inconsistent price values detected"
        
    return True, ""

def validate_parameters(strategy_id: str, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate strategy parameters
    
    Args:
        strategy_id: Strategy identifier
        parameters: Strategy parameters to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if strategy_id == 'moving_average':
        required_params = ['short_window', 'long_window']
        for param in required_params:
            if param not in parameters:
                errors.append(f"Missing required parameter: {param}")
                continue
            
            value = parameters[param]
            if not isinstance(value, (int, float)):
                errors.append(f"{param} must be a number")
            elif value <= 0:
                errors.append(f"{param} must be greater than 0")
                
        if not errors and parameters['short_window'] >= parameters['long_window']:
            errors.append("Short window must be less than long window")
            
    elif strategy_id == 'rsi':
        required_params = ['period', 'overbought', 'oversold']
        for param in required_params:
            if param not in parameters:
                errors.append(f"Missing required parameter: {param}")
                continue
                
            value = parameters[param]
            if not isinstance(value, (int, float)):
                errors.append(f"{param} must be a number")
            elif param == 'period' and value <= 0:
                errors.append("Period must be greater than 0")
            elif param in ['overbought', 'oversold']:
                if not 0 <= value <= 100:
                    errors.append(f"{param} must be between 0 and 100")
                    
        if not errors:
            if parameters['oversold'] >= parameters['overbought']:
                errors.append("Oversold level must be less than overbought level")
    
    return len(errors) == 0, errors

def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, List[str]]:
    """Validate date range
    
    Args:
        start_date: Start date string (ISO format)
        end_date: End date string (ISO format)
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        if start >= end:
            errors.append("Start date must be before end date")
            
        # Check if dates are too far in the past or future
        now = pd.Timestamp.now()
        if start > now:
            errors.append("Start date cannot be in the future")
        if end > now:
            errors.append("End date cannot be in the future")
            
        max_days = 365 * 5  # 5 years
        if (end - start).days > max_days:
            errors.append(f"Date range cannot exceed {max_days} days")
            
    except ValueError as e:
        errors.append(f"Invalid date format: {str(e)}")
        
    return len(errors) == 0, errors

def validate_market_data(data: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate market data
    
    Args:
        data: DataFrame containing market data
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
    if not errors:
        # Check for missing values
        na_columns = data.columns[data.isna().any()].tolist()
        if na_columns:
            errors.append(f"Missing values in columns: {', '.join(na_columns)}")
            
        # Check for invalid values
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if (data[col] <= 0).any():
                errors.append(f"Invalid values (<=0) in column: {col}")
                
        # Check price consistency
        invalid_prices = (
            (data['low'] > data['high']) |
            (data['open'] > data['high']) |
            (data['open'] < data['low']) |
            (data['close'] > data['high']) |
            (data['close'] < data['low'])
        )
        if invalid_prices.any():
            errors.append("Inconsistent price values detected")
            
    return len(errors) == 0, errors 

def validate_backtest_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate backtesting parameters
    
    Args:
        params: Dictionary containing backtest parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_params = ['start_date', 'end_date', 'initial_balance']
    
    # Check required parameters
    for param in required_params:
        if param not in params:
            return False, f"Missing required parameter: {param}"
    
    # Validate dates
    try:
        start_date = datetime.strptime(params['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(params['end_date'], '%Y-%m-%d')
        
        if start_date >= end_date:
            return False, "Start date must be before end date"
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"
    
    # Validate initial balance
    if not isinstance(params['initial_balance'], (int, float)) or params['initial_balance'] <= 0:
        return False, "Initial balance must be a positive number"
    
    return True, "" 