from typing import List, Dict, Any
import pandas as pd
import pandas_ta as ta
import numpy as np

class TechnicalFeatureGenerator:
    """Generate technical analysis features for ML models"""
    
    @staticmethod
    def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add basic price-based features"""
        df = df.copy()
        
        # Returns
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log1p(df['returns'])
        
        # Price ratios
        df['hl_ratio'] = df['high'] / df['low']
        df['co_ratio'] = df['close'] / df['open']
        
        # Volume features
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_std'] = df['volume'].rolling(window=20).std()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        return df
        
    @staticmethod
    def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum indicators"""
        df = df.copy()
        
        # RSI
        df['rsi'] = df['close'].ta.rsi(length=14)
        
        # MACD
        macd = df.ta.macd(fast=12, slow=26, signal=9)
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        df['macd_hist'] = macd['MACDh_12_26_9']
        
        # Stochastic
        stoch = df.ta.stoch(high='high', low='low', close='close')
        df['stoch_k'] = stoch['STOCHk_14_3_3']
        df['stoch_d'] = stoch['STOCHd_14_3_3']
        
        return df
        
    @staticmethod
    def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility indicators"""
        df = df.copy()
        
        # Bollinger Bands
        bb = df.ta.bbands(length=20)
        df['bb_upper'] = bb['BBU_20_2.0']
        df['bb_middle'] = bb['BBM_20_2.0']
        df['bb_lower'] = bb['BBL_20_2.0']
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # ATR
        df['atr'] = df.ta.atr(length=14)
        
        # Historical volatility
        df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
        
        return df
        
    @staticmethod
    def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add trend indicators"""
        df = df.copy()
        
        # Moving averages
        for period in [5, 10, 20, 50, 200]:
            df[f'sma_{period}'] = df['close'].ta.sma(length=period)
            df[f'ema_{period}'] = df['close'].ta.ema(length=period)
        
        # ADX
        adx = df.ta.adx()
        df['adx'] = adx['ADX_14']
        
        # Ichimoku Cloud
        ichimoku = df.ta.ichimoku()
        df['tenkan_sen'] = ichimoku['ITS_9']
        df['kijun_sen'] = ichimoku['IKS_26']
        
        return df
        
    @classmethod
    def generate_features(cls, 
                         df: pd.DataFrame,
                         feature_sets: List[str] = None) -> pd.DataFrame:
        """Generate all or specified feature sets"""
        if feature_sets is None:
            feature_sets = ['price', 'momentum', 'volatility', 'trend']
            
        df = df.copy()
        
        feature_generators = {
            'price': cls.add_price_features,
            'momentum': cls.add_momentum_features,
            'volatility': cls.add_volatility_features,
            'trend': cls.add_trend_features
        }
        
        for feature_set in feature_sets:
            if feature_set in feature_generators:
                df = feature_generators[feature_set](df)
                
        # Drop rows with NaN values
        df = df.dropna()
        
        return df 