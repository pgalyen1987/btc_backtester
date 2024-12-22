from finta import TA
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=128)
def calculate_indicator(indicator_type: str, values: tuple, period: int) -> np.ndarray:
    """Cached calculation of individual indicators"""
    values_array = np.array(values)
    if indicator_type == 'sma':
        return pd.Series(values_array).rolling(window=period).mean().values
    elif indicator_type == 'ema':
        return pd.Series(values_array).ewm(span=period, adjust=False).mean().values
    return np.array([])

def add_indicators(df, indicators=None):
    """
    Add technical indicators to the dataframe
    
    Args:
        df (pandas.DataFrame): Price data
        indicators (dict): Dictionary of indicators to add with their parameters
                         e.g., {'SMA': [20, 50], 'RSI': [14], 'MACD': None}
    
    Returns:
        pandas.DataFrame: DataFrame with added indicators
    """
    if indicators is None:
        indicators = {
            'SMA': [20],
            'EMA': [20],
            'RSI': [14],
            'MACD': None,
            'BBANDS': None
        }

    df = df.copy()
    
    for indicator, params in indicators.items():
        if indicator == 'SMA':
            for period in params:
                df[f'SMA_{period}'] = TA.SMA(df, period)
        
        elif indicator == 'EMA':
            for period in params:
                df[f'EMA_{period}'] = TA.EMA(df, period)
        
        elif indicator == 'RSI':
            for period in params:
                df[f'RSI_{period}'] = TA.RSI(df, period)
        
        elif indicator == 'MACD':
            macd = TA.MACD(df)
            df['MACD'] = macd['MACD']
            df['MACD_SIGNAL'] = macd['SIGNAL']
            df['MACD_HIST'] = df['MACD'] - df['MACD_SIGNAL']
        
        elif indicator == 'BBANDS':
            bbands = TA.BBANDS(df)
            df['BB_UPPER'] = bbands['BB_UPPER']
            df['BB_MIDDLE'] = bbands['BB_MIDDLE']
            df['BB_LOWER'] = bbands['BB_LOWER']
            # Add BB squeeze indicator
            df['BB_SQUEEZE'] = (df['BB_UPPER'] - df['BB_LOWER']) / df['BB_MIDDLE']
        
        elif indicator == 'STOCH':
            for period in params:
                df[f'STOCH_{period}'] = TA.STOCH(df, period)
                df[f'STOCH_SIGNAL_{period}'] = df[f'STOCH_{period}'].rolling(window=3).mean()
        
        elif indicator == 'ADX':
            for period in params:
                df[f'ADX_{period}'] = TA.ADX(df, period)
        
        elif indicator == 'ATR':
            for period in params:
                df[f'ATR_{period}'] = TA.ATR(df, period)
        
        elif indicator == 'VWAP':
            df['VWAP'] = TA.VWAP(df)
        
        elif indicator == 'OBV':
            df['OBV'] = TA.OBV(df)
        
        elif indicator == 'SUPPORT_RESISTANCE':
            # Simple support and resistance levels using rolling min/max
            period = params[0] if params else 20
            df[f'SUPPORT_{period}'] = df['Low'].rolling(window=period).min()
            df[f'RESISTANCE_{period}'] = df['High'].rolling(window=period).max()
        
        elif indicator == 'VOLATILITY':
            # Various volatility indicators
            for period in params:
                # Standard deviation of returns
                df[f'VOL_STD_{period}'] = df['Close'].pct_change().rolling(period).std()
                # Normalized ATR
                df[f'VOL_NATR_{period}'] = TA.ATR(df, period) / df['Close']
        
        elif indicator == 'MOMENTUM':
            for period in params:
                # ROC (Rate of Change)
                df[f'ROC_{period}'] = TA.ROC(df, period)
                # Momentum
                df[f'MOM_{period}'] = df['Close'].diff(period)
        
        elif indicator == 'ICHIMOKU':
            ichimoku = TA.ICHIMOKU(df)
            for key in ['TENKAN', 'KIJUN', 'SENKOU_A', 'SENKOU_B']:
                if key in ichimoku:
                    df[f'ICH_{key}'] = ichimoku[key]
        
        elif indicator == 'PATTERNS':
            # Add candlestick patterns
            df['DOJI'] = TA.CDLDOJI(df) if hasattr(TA, 'CDLDOJI') else 0
            df['HAMMER'] = TA.CDLHAMMER(df) if hasattr(TA, 'CDLHAMMER') else 0
            df['SHOOTING_STAR'] = TA.CDLSHOOTINGSTAR(df) if hasattr(TA, 'CDLSHOOTINGSTAR') else 0
            df['ENGULFING'] = TA.CDLENGULFING(df) if hasattr(TA, 'CDLENGULFING') else 0
            
    return df

def calculate_pivots(df, method='standard'):
    """
    Calculate pivot points using different methods
    
    Args:
        df (pandas.DataFrame): Price data
        method (str): Pivot calculation method ('standard', 'fibonacci', 'woodie', 'camarilla')
    
    Returns:
        pandas.DataFrame: DataFrame with pivot points
    """
    df = df.copy()
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    if method == 'standard':
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
    elif method == 'fibonacci':
        pivot = (high + low + close) / 3
        r1 = pivot + 0.382 * (high - low)
        s1 = pivot - 0.382 * (high - low)
        r2 = pivot + 0.618 * (high - low)
        s2 = pivot - 0.618 * (high - low)
        r3 = pivot + (high - low)
        s3 = pivot - (high - low)
        
        df['PP_FIB_R3'] = r3
        df['PP_FIB_S3'] = s3
    
    elif method == 'woodie':
        pivot = (high + low + 2 * close) / 4
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + high - low
        s2 = pivot - (high - low)
    
    elif method == 'camarilla':
        pivot = (high + low + close) / 3
        r1 = close + 1.1 * (high - low) / 12
        s1 = close - 1.1 * (high - low) / 12
        r2 = close + 1.1 * (high - low) / 6
        s2 = close - 1.1 * (high - low) / 6
        r3 = close + 1.1 * (high - low) / 4
        s3 = close - 1.1 * (high - low) / 4
        
        df['PP_CAM_R3'] = r3
        df['PP_CAM_S3'] = s3
    
    df[f'PP_{method.upper()}'] = pivot
    df[f'PP_{method.upper()}_R1'] = r1
    df[f'PP_{method.upper()}_S1'] = s1
    df[f'PP_{method.upper()}_R2'] = r2
    df[f'PP_{method.upper()}_S2'] = s2
    
    return df 

def add_technical_indicators(df: pd.DataFrame, indicators: Dict[str, Any]) -> pd.DataFrame:
    """Optimized version of technical indicators calculation"""
    df = df.copy()
    close_values = tuple(df['Close'].values)  # Convert to tuple for caching
    
    for indicator, params in indicators.items():
        if indicator == 'SMA':
            for period in params:
                df[f'SMA_{period}'] = calculate_indicator('sma', close_values, period)
                
        elif indicator == 'EMA':
            for period in params:
                df[f'EMA_{period}'] = calculate_indicator('ema', close_values, period)
                
        elif indicator == 'RSI':
            for period in params:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
                
        elif indicator == 'MACD':
            fast, slow, signal = params
            # Calculate MACD components in one pass
            df['MACD'] = calculate_indicator('ema', close_values, fast) - \
                        calculate_indicator('ema', close_values, slow)
            df['MACD_Signal'] = pd.Series(df['MACD']).ewm(span=signal, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    return df.dropna()