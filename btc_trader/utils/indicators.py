"""Technical indicators module for BTC Trader"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, Any, Optional, List

def add_technical_indicators(df: pd.DataFrame, indicators: Dict[str, List[int]]) -> pd.DataFrame:
    """Add technical indicators to DataFrame
    
    Args:
        df: DataFrame with OHLCV data
        indicators: Dictionary of indicators and their parameters
        
    Returns:
        DataFrame with added indicators
    """
    df = df.copy()
    
    for indicator, params in indicators.items():
        if indicator == 'SMA':
            for period in params:
                df[f'SMA_{period}'] = df['Close'].ta.sma(length=period)
        elif indicator == 'EMA':
            for period in params:
                df[f'EMA_{period}'] = df['Close'].ta.ema(length=period)
        elif indicator == 'RSI':
            for period in params:
                df[f'RSI_{period}'] = df['Close'].ta.rsi(length=period)
        elif indicator == 'MACD':
            fast_period, slow_period, signal_period = params
            macd = df.ta.macd(fast=fast_period, slow=slow_period, signal=signal_period)
            df['MACD'] = macd[f'MACD_{fast_period}_{slow_period}_{signal_period}']
            df['MACD_SIGNAL'] = macd[f'MACDs_{fast_period}_{slow_period}_{signal_period}']
            df['MACD_HIST'] = macd[f'MACDh_{fast_period}_{slow_period}_{signal_period}']
        elif indicator == 'BB':
            for period in params:
                bb = df.ta.bbands(length=period)
                df[f'BB_UPPER_{period}'] = bb[f'BBU_{period}_2.0']
                df[f'BB_MIDDLE_{period}'] = bb[f'BBM_{period}_2.0']
                df[f'BB_LOWER_{period}'] = bb[f'BBL_{period}_2.0']
    
    return df

def calculate_pivots(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """Calculate pivot points and support/resistance levels
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for pivot calculation
        
    Returns:
        DataFrame with pivot points and levels
    """
    df = df.copy()
    
    # Use pandas-ta's pivot points
    pivots = df.ta.pivots(high='High', low='Low', close='Close', period=period)
    
    # Rename columns to match existing code
    df['PP'] = pivots[f'PP_{period}']
    df['S1'] = pivots[f'S1_{period}']
    df['S2'] = pivots[f'S2_{period}']
    df['R1'] = pivots[f'R1_{period}']
    df['R2'] = pivots[f'R2_{period}']
    
    return df

__all__ = ['add_technical_indicators', 'calculate_pivots']