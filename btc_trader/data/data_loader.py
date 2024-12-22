import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DataLoader:
    """Data loader for fetching and managing price data"""
    
    def __init__(self, default_symbol: str = "BTC-USD"):
        """Initialize data loader
        
        Args:
            default_symbol (str): Default trading symbol to use
        """
        self.default_symbol = default_symbol
        self._data_cache = {}
    
    def fetch_data(self, 
                  period_days: int = 365,
                  interval: str = '1d',
                  symbol: Optional[str] = None) -> pd.DataFrame:
        """Fetch historical price data from Yahoo Finance
        
        Args:
            period_days (int): Number of days of historical data to fetch
            interval (str): Data interval ('1m', '5m', '15m', '1h', '4h', '1d')
            symbol (str, optional): Trading symbol (e.g., 'BTC-USD'). Uses default if not provided
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
            
        Raises:
            ValueError: If parameters are invalid or data fetch fails
        """
        try:
            # Validate parameters
            if period_days <= 0:
                raise ValueError("Period days must be positive")
            
            valid_intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
            if interval not in valid_intervals:
                raise ValueError(f"Interval must be one of: {valid_intervals}")
            
            # Use default symbol if none provided
            symbol = symbol or self.default_symbol
            
            # Check cache
            cache_key = f"{symbol}_{period_days}_{interval}"
            if cache_key in self._data_cache:
                cached_data = self._data_cache[cache_key]
                if (datetime.now() - cached_data['timestamp']).total_seconds() < 3600:  # 1 hour cache
                    return cached_data['data']
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Fetch data from Yahoo Finance
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            if data.empty:
                raise ValueError(f"No data received for {symbol}")
            
            # Ensure all required columns are present
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Clean and prepare data
            data = data[required_columns].copy()  # Only keep required columns
            data = data.ffill()  # Forward fill missing values
            data = data.dropna()  # Remove any remaining NaN rows
            
            # Update cache
            self._data_cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            # Manage cache size
            if len(self._data_cache) > 10:  # Keep only 10 most recent datasets
                oldest_key = min(self._data_cache.keys(), 
                               key=lambda k: self._data_cache[k]['timestamp'])
                del self._data_cache[oldest_key]
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise ValueError(f"Failed to fetch data: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear the data cache"""
        self._data_cache.clear()
        logger.info("Data cache cleared")

    def get_latest_data(self):
        """Get the most recent data point"""
        if self.data is not None and not self.data.empty:
            return self.data.iloc[-1]
        return None

    def get_data_range(self, start_idx, end_idx):
        """Get a specific range of data"""
        if self.data is not None:
            return self.data.iloc[start_idx:end_idx]
        return None 