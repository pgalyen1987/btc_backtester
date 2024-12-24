import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Tuple
import numpy as np
import time
import hashlib
import json

logger = logging.getLogger(__name__)

class DataLoader:
    """Data loader class for fetching and preparing trading data"""
    
    def __init__(self, symbol: str = 'BTC-USD'):
        """Initialize the data loader
        
        Args:
            symbol: Trading symbol to use (default: BTC-USD)
        """
        self.symbol = symbol
        self._cache = {}  # Cache dictionary to store data for different periods/intervals
        self._last_fetch = {}  # Track last fetch time for each cache key
        self._cache_duration = timedelta(minutes=15)  # Cache duration
        logger.info(f"Initialized DataLoader for symbol: {symbol}")
    
    def _get_cache_key(self, period_days: int, interval: str) -> str:
        """Generate a unique cache key for the given parameters"""
        params = {
            'symbol': self.symbol,
            'period_days': period_days,
            'interval': interval
        }
        key = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        return key
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._last_fetch:
            return False
        
        time_since_fetch = datetime.now() - self._last_fetch[cache_key]
        return time_since_fetch < self._cache_duration
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """Validate the fetched data"""
        if df is None or df.empty:
            logger.warning("Received empty DataFrame")
            return False
            
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
            
        if len(df) < 2:
            logger.warning("Insufficient data points")
            return False
            
        null_columns = df[required_columns].isnull().all()
        if null_columns.any():
            logger.warning(f"Columns with all null values: {null_columns[null_columns].index.tolist()}")
            return False
        
        zero_columns = (df[required_columns] == 0).all()
        if zero_columns.any():
            logger.warning(f"Columns with all zero values: {zero_columns[zero_columns].index.tolist()}")
            return False
        
        logger.debug(f"Data validation passed. Shape: {df.shape}")
        return True
    
    def load_data(self, period_days: int = 365, interval: str = '1d') -> pd.DataFrame:
        """Load trading data for the specified period and interval"""
        try:
            cache_key = self._get_cache_key(period_days, interval)
            
            # Check cache first
            if cache_key in self._cache and self._is_cache_valid(cache_key):
                logger.info(f"Using cached data for {self.symbol}")
                return self._cache[cache_key]
            
            logger.info(f"Fetching new data for {self.symbol} (period: {period_days} days, interval: {interval})")
            
            # Validate interval
            valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
            if interval not in valid_intervals:
                logger.warning(f"Invalid interval: {interval}, using '1d'")
                interval = '1d'
            
            # Convert period_days to yfinance period format
            if period_days <= 7:
                period = f"{period_days}d"
            elif period_days <= 30:
                period = "1mo"
            elif period_days <= 90:
                period = "3mo"
            elif period_days <= 180:
                period = "6mo"
            elif period_days <= 365:
                period = "1y"
            elif period_days <= 730:
                period = "2y"
            else:
                period = "max"
            
            # Try to download data with retries
            max_retries = 3
            retry_delay = 2  # seconds
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    logger.debug(f"Download attempt {attempt + 1}/{max_retries}")
                    df = yf.download(
                        self.symbol,
                        period=period,
                        interval=interval,
                        progress=False,
                        show_errors=True,
                        timeout=10  # Add timeout to prevent hanging
                    )
                    
                    if df is None:
                        raise ValueError(f"yfinance returned None for {self.symbol}")
                    
                    if df.empty:
                        raise ValueError(f"yfinance returned empty DataFrame for {self.symbol}")
                    
                    if self._validate_data(df):
                        logger.info(f"Successfully downloaded {len(df)} data points")
                        break
                    else:
                        raise ValueError(f"Downloaded data failed validation for {self.symbol}")
                        
                except Exception as e:
                    last_error = e
                    logger.error(f"Download attempt {attempt + 1} failed: {str(e)}", exc_info=True)
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    raise ValueError(f"All download attempts failed for {self.symbol}") from last_error
            
            # Add technical indicators
            try:
                df = self._add_indicators(df)
            except Exception as e:
                logger.error("Error adding technical indicators:", exc_info=True)
                raise ValueError(f"Failed to add technical indicators: {str(e)}") from e
            
            # Update cache
            self._cache[cache_key] = df
            self._last_fetch[cache_key] = datetime.now()
            
            logger.info(f"Successfully processed data with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error in load_data: {str(e)}", exc_info=True)
            raise  # Re-raise to preserve the original error context
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""
        try:
            logger.debug("Adding technical indicators")
            
            # Make a copy to avoid modifying the original
            df = df.copy()
            
            # Calculate moving averages (with minimum periods)
            df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
            df['SMA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
            
            # Calculate RSI (with minimum periods)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            rs = gain / loss.replace(0, np.inf)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            exp1 = df['Close'].ewm(span=12, adjust=False, min_periods=1).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False, min_periods=1).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False, min_periods=1).mean()
            
            # Calculate Bollinger Bands (with minimum periods)
            df['BB_middle'] = df['Close'].rolling(window=20, min_periods=1).mean()
            bb_std = df['Close'].rolling(window=20, min_periods=1).std()
            df['BB_upper'] = df['BB_middle'] + 2 * bb_std
            df['BB_lower'] = df['BB_middle'] - 2 * bb_std
            
            # Calculate ATR (with minimum periods)
            high_low = df['High'] - df['Low']
            high_close = abs(df['High'] - df['Close'].shift())
            low_close = abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['ATR'] = true_range.rolling(window=14, min_periods=1).mean()
            
            # Volume indicators (with minimum periods)
            df['Volume_SMA'] = df['Volume'].rolling(window=20, min_periods=1).mean()
            df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
            
            # Fill any remaining NaN values with forward fill then backward fill
            df = df.fillna(method='ffill').fillna(method='bfill')
            
            logger.debug(f"Added indicators. Final columns: {df.columns.tolist()}")
            logger.debug(f"Final data shape: {df.shape}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding indicators: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to add indicators: {str(e)}")
    
    def get_latest_price(self) -> Optional[float]:
        """Get the latest price for the symbol"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                price = float(data['Close'].iloc[-1])
                logger.info(f"Latest price for {self.symbol}: {price}")
                return price
        except Exception as e:
            logger.error(f"Error getting latest price: {str(e)}")
        return None