"""Technical indicators module"""
import pandas as pd
import pandas_ta as ta
from typing import Dict, Any

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to the dataframe
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added technical indicators
    """
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    try:
        # Moving Averages
        df['sma_20'] = df['close'].ta.sma(length=20)
        df['sma_50'] = df['close'].ta.sma(length=50)
        df['sma_200'] = df['close'].ta.sma(length=200)
        df['ema_12'] = df['close'].ta.ema(length=12)
        df['ema_26'] = df['close'].ta.ema(length=26)
        
        # Momentum Indicators
        df['rsi'] = df['close'].ta.rsi(length=14)
        macd = df.ta.macd(fast=12, slow=26, signal=9)
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        df['macd_hist'] = macd['MACDh_12_26_9']
        
        # Volatility Indicators
        bb = df.ta.bbands(length=20)
        df['bb_upper'] = bb['BBU_20_2.0']
        df['bb_middle'] = bb['BBM_20_2.0']
        df['bb_lower'] = bb['BBL_20_2.0']
        df['atr'] = df.ta.atr(length=14)
        
        # Volume Indicators
        df['obv'] = df.ta.obv()
        df['vwap'] = df.ta.vwap()
        
        # Trend Indicators
        df['adx'] = df.ta.adx()
        
    except Exception as e:
        raise ValueError(f"Error calculating technical indicators: {str(e)}")
    
    # Fill any remaining NaN values with forward fill then backward fill
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    return df