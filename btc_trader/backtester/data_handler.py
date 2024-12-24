from typing import Dict, Any, Optional
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch_historical_data(self, 
                            symbol: str,
                            start_date: datetime,
                            end_date: datetime,
                            interval: str) -> pd.DataFrame:
        """Fetch historical price data"""
        pass
        
    @abstractmethod
    def fetch_live_data(self, symbol: str, interval: str) -> pd.DataFrame:
        """Fetch live price data"""
        pass

class YFinanceDataSource(DataSource):
    """Yahoo Finance data source implementation"""
    
    def fetch_historical_data(self,
                            symbol: str,
                            start_date: datetime,
                            end_date: datetime,
                            interval: str) -> pd.DataFrame:
        """Fetch historical price data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            # Rename columns to standard format
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Add timestamp column
            data['timestamp'] = data.index
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
            
    def fetch_live_data(self, symbol: str, interval: str) -> pd.DataFrame:
        """Fetch live price data from Yahoo Finance"""
        try:
            # For Yahoo Finance, we'll fetch the most recent data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            return self.fetch_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            
        except Exception as e:
            logger.error(f"Error fetching live data: {e}")
            raise

class DataHandler:
    """Handler for managing price data"""
    
    def __init__(self, data_source: DataSource = None):
        self.data_source = data_source or YFinanceDataSource()
        self.cache = {}
        
    def get_historical_data(self,
                          symbol: str,
                          period_days: int,
                          interval: str,
                          use_cache: bool = True) -> pd.DataFrame:
        """Get historical price data"""
        cache_key = f"{symbol}_{period_days}_{interval}"
        
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        data = self.data_source.fetch_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        if use_cache:
            self.cache[cache_key] = data
            
        return data
        
    def get_live_data(self, symbol: str, interval: str) -> pd.DataFrame:
        """Get live price data"""
        return self.data_source.fetch_live_data(
            symbol=symbol,
            interval=interval
        )
        
    def clear_cache(self):
        """Clear the data cache"""
        self.cache = {} 