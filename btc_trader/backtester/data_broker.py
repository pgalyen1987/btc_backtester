from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import yfinance as yf
from .data_handler import DataSource

logger = logging.getLogger(__name__)

class DataBroker:
    """Centralized data broker using Arctic for efficient data management"""
    
    def __init__(self, mongo_host: str = 'localhost', mongo_port: int = 27017):
        """Initialize data broker with MongoDB connection"""
        self.store = Arctic(f'mongodb://{mongo_host}:{mongo_port}/')
        self._initialize_libraries()
        
    def _initialize_libraries(self):
        """Initialize Arctic libraries for different data types"""
        libraries = {
            'MARKET_DATA': CHUNK_STORE,  # Market data (OHLCV)
            'FEATURES': CHUNK_STORE,     # Technical indicators and features
            'METADATA': CHUNK_STORE      # Symbol metadata and info
        }
        
        for lib_name, lib_type in libraries.items():
            try:
                self.store.get_library(lib_name)
            except LibraryNotFoundException:
                self.store.initialize_library(lib_name, lib_type=lib_type)
                
    def write_market_data(self, 
                         symbol: str, 
                         data: pd.DataFrame,
                         metadata: Dict[str, Any] = None):
        """Write market data to storage"""
        try:
            library = self.store['MARKET_DATA']
            library.write(symbol, data, metadata=metadata)
            logger.info(f"Successfully wrote market data for {symbol}")
        except Exception as e:
            logger.error(f"Error writing market data for {symbol}: {e}")
            raise
            
    def read_market_data(self,
                        symbol: str,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Read market data from storage"""
        try:
            library = self.store['MARKET_DATA']
            data = library.read(symbol, chunk_range=(start_date, end_date))
            return data.data
        except Exception as e:
            logger.error(f"Error reading market data for {symbol}: {e}")
            raise
            
    def write_features(self,
                      symbol: str,
                      features: pd.DataFrame,
                      feature_set: str,
                      metadata: Dict[str, Any] = None):
        """Write feature data to storage"""
        try:
            library = self.store['FEATURES']
            key = f"{symbol}_{feature_set}"
            library.write(key, features, metadata=metadata)
            logger.info(f"Successfully wrote features for {key}")
        except Exception as e:
            logger.error(f"Error writing features for {symbol}: {e}")
            raise
            
    def read_features(self,
                     symbol: str,
                     feature_set: str,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Read feature data from storage"""
        try:
            library = self.store['FEATURES']
            key = f"{symbol}_{feature_set}"
            features = library.read(key, chunk_range=(start_date, end_date))
            return features.data
        except Exception as e:
            logger.error(f"Error reading features for {symbol}: {e}")
            raise
            
    def update_market_data(self,
                          symbol: str,
                          data_source: DataSource,
                          interval: str = '1d'):
        """Update market data with latest available data"""
        try:
            # Get existing data
            try:
                existing_data = self.read_market_data(symbol)
                last_date = existing_data.index[-1]
            except:
                existing_data = None
                last_date = None
                
            # Fetch new data
            end_date = datetime.now()
            start_date = last_date + timedelta(days=1) if last_date else end_date - timedelta(days=365)
            
            new_data = data_source.fetch_historical_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            
            # Combine and deduplicate data
            if existing_data is not None:
                data = pd.concat([existing_data, new_data])
                data = data[~data.index.duplicated(keep='last')]
            else:
                data = new_data
                
            # Write updated data
            self.write_market_data(
                symbol=symbol,
                data=data,
                metadata={
                    'last_updated': datetime.now(),
                    'interval': interval
                }
            )
            
            logger.info(f"Successfully updated market data for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error updating market data for {symbol}: {e}")
            raise
            
    def get_symbols(self) -> List[str]:
        """Get list of available symbols"""
        try:
            library = self.store['MARKET_DATA']
            return library.list_symbols()
        except Exception as e:
            logger.error(f"Error getting symbol list: {e}")
            raise
            
    def get_feature_sets(self, symbol: str) -> List[str]:
        """Get list of available feature sets for a symbol"""
        try:
            library = self.store['FEATURES']
            all_keys = library.list_symbols()
            return [key.split('_')[1] for key in all_keys if key.startswith(f"{symbol}_")]
        except Exception as e:
            logger.error(f"Error getting feature sets for {symbol}: {e}")
            raise 