"""Feature engineering for ML models"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from ...utils.indicators import add_technical_indicators

class FeatureEngineer:
    """Feature engineering for ML models"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize feature engineer
        
        Args:
            config: Configuration dictionary with parameters:
                - technical_indicators: Dict of indicators to add
                - window_sizes: List of window sizes for rolling features
                - target_column: Name of target column
        """
        self.config = config or {}
        self.technical_indicators = config.get('technical_indicators', {
            'SMA': [20, 50],
            'RSI': [14],
            'MACD': [12, 26, 9]
        })
        self.window_sizes = config.get('window_sizes', [5, 10, 20])
        self.target_column = config.get('target_column', 'Close')
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create features from raw data
        
        Args:
            data: Raw price data
            
        Returns:
            DataFrame with engineered features
        """
        df = data.copy()
        
        # Add technical indicators
        df = add_technical_indicators(df, self.technical_indicators)
        
        # Add rolling statistics
        for window in self.window_sizes:
            df[f'rolling_mean_{window}'] = df[self.target_column].rolling(window=window).mean()
            df[f'rolling_std_{window}'] = df[self.target_column].rolling(window=window).std()
            df[f'rolling_min_{window}'] = df[self.target_column].rolling(window=window).min()
            df[f'rolling_max_{window}'] = df[self.target_column].rolling(window=window).max()
        
        # Add price momentum
        df['price_momentum'] = df[self.target_column].pct_change()
        
        # Add volatility
        df['volatility'] = df[self.target_column].rolling(window=20).std()
        
        # Add volume features
        if 'Volume' in df.columns:
            df['volume_momentum'] = df['Volume'].pct_change()
            df['volume_ma'] = df['Volume'].rolling(window=20).mean()
            df['volume_std'] = df['Volume'].rolling(window=20).std()
        
        # Add time-based features
        if isinstance(df.index, pd.DatetimeIndex):
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
        
        # Drop rows with NaN values
        df = df.dropna()
        
        return df
    
    def create_target(self, data: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
        """Create target variable for prediction
        
        Args:
            data: Price data
            horizon: Number of periods ahead to predict
            
        Returns:
            DataFrame with target variable
        """
        df = data.copy()
        
        # Create future returns
        df['target'] = df[self.target_column].shift(-horizon)
        
        # Create binary classification target
        df['target_direction'] = (df['target'] > df[self.target_column]).astype(int)
        
        # Drop last 'horizon' rows since we don't have targets for them
        df = df.iloc[:-horizon]
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names
        
        Returns:
            List of feature column names
        """
        # This is a placeholder - actual feature names would depend on
        # the features created in create_features
        return [
            'technical_indicators',
            'rolling_statistics',
            'momentum_features',
            'volume_features',
            'time_features'
        ] 