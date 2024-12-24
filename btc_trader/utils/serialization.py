"""Utilities for data serialization"""
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def serialize_numpy(obj: Any) -> Union[int, float, bool, list, None]:
    """Convert numpy types to Python native types for JSON serialization"""
    try:
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32,
                          np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.void, pd.NA, pd.NaT)):
            return None
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        return obj
    except Exception as e:
        logger.error(f"Error in serialize_numpy: {str(e)}")
        return None

def serialize_dataframe(df: pd.DataFrame, date_format: str = 'iso') -> Dict[str, Any]:
    """Serialize a pandas DataFrame to a dictionary"""
    try:
        result = {}
        for column in df.columns:
            series = df[column]
            if pd.api.types.is_datetime64_any_dtype(series):
                result[column] = series.dt.strftime(date_format) if date_format != 'iso' else series.dt.isoformat()
            else:
                result[column] = [serialize_numpy(val) for val in series]
        return result
    except Exception as e:
        logger.error(f"Error serializing DataFrame: {str(e)}")
        return {}

def serialize_trade(trade: Any) -> Dict[str, Any]:
    """Serialize a trade object to a dictionary"""
    try:
        return {
            'timestamp': trade.timestamp.isoformat() if hasattr(trade, 'timestamp') else None,
            'type': trade.type if hasattr(trade, 'type') else None,
            'price': serialize_numpy(trade.price) if hasattr(trade, 'price') else None,
            'amount': serialize_numpy(trade.amount) if hasattr(trade, 'amount') else None,
            'value': serialize_numpy(trade.value) if hasattr(trade, 'value') else None,
            'fees': serialize_numpy(trade.fees) if hasattr(trade, 'fees') else None,
            'pnl': serialize_numpy(trade.pnl) if hasattr(trade, 'pnl') else None
        }
    except Exception as e:
        logger.error(f"Error serializing trade: {str(e)}")
        return {}

def serialize_backtest_result(result: Any) -> Dict[str, Any]:
    """Serialize a backtest result to a dictionary"""
    try:
        return {
            'portfolio': serialize_dataframe(result.portfolio) if hasattr(result, 'portfolio') else {},
            'trades': [serialize_trade(trade) for trade in result.trades] if hasattr(result, 'trades') else [],
            'metrics': {
                'total_return': serialize_numpy(result.total_return),
                'sharpe_ratio': serialize_numpy(result.sharpe_ratio),
                'max_drawdown': serialize_numpy(result.max_drawdown),
                'win_rate': serialize_numpy(result.win_rate),
                'profit_factor': serialize_numpy(result.profit_factor)
            } if hasattr(result, 'metrics') else {}
        }
    except Exception as e:
        logger.error(f"Error serializing backtest result: {str(e)}")
        return {} 