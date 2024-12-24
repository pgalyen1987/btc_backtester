"""Prophet model for time series prediction"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
import logging
from .base_model import BaseModel

logger = logging.getLogger(__name__)

class ProphetModel(BaseModel):
    """Prophet model for time series prediction"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Prophet model
        
        Args:
            config: Model configuration dictionary with parameters:
                - changepoint_prior_scale: Flexibility of the trend
                - seasonality_prior_scale: Flexibility of the seasonality
                - holidays_prior_scale: Flexibility of the holiday effects
                - seasonality_mode: Type of seasonality ('additive' or 'multiplicative')
        """
        super().__init__(config)
        config = config or {}
        try:
            self.model = Prophet(
                changepoint_prior_scale=config.get('changepoint_prior_scale', 0.05),
                seasonality_prior_scale=config.get('seasonality_prior_scale', 10.0),
                holidays_prior_scale=config.get('holidays_prior_scale', 10.0),
                seasonality_mode=config.get('seasonality_mode', 'additive')
            )
        except Exception as e:
            logger.error(f"Error initializing Prophet model: {e}")
            self.model = None
    
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data for Prophet model
        
        Args:
            data: DataFrame with datetime index and target column
            
        Returns:
            DataFrame in Prophet format (ds, y)
            
        Raises:
            ValueError: If data format is invalid
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        if 'Close' not in data.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        df = data.copy()
        
        try:
            # Ensure index is datetime
            if not isinstance(df.index, pd.DatetimeIndex):
                raise ValueError("DataFrame index must be DatetimeIndex")
            
            # Prophet requires columns named 'ds' and 'y'
            df['ds'] = df.index
            df['y'] = df['Close']
            
            # Handle missing values
            df = df.dropna(subset=['ds', 'y'])
            
            if len(df) == 0:
                raise ValueError("No valid data points after preprocessing")
            
            return df[['ds', 'y']]
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            raise
    
    def train(self, data: pd.DataFrame) -> Dict[str, float]:
        """Train Prophet model
        
        Args:
            data: Training data
            
        Returns:
            Dictionary of training metrics
            
        Raises:
            RuntimeError: If model initialization failed
            ValueError: If data is invalid
        """
        if self.model is None:
            raise RuntimeError("Model not properly initialized")
            
        try:
            # Preprocess data
            processed_data = self.preprocess(data)
            
            # Train model
            self.model.fit(processed_data)
            
            # Make in-sample predictions for metrics
            predictions = self.model.predict(processed_data)
            y_true = processed_data['y'].values
            y_pred = predictions['yhat'].values
            
            # Calculate metrics
            mse = np.mean((y_true - y_pred) ** 2)
            mae = np.mean(np.abs(y_true - y_pred))
            rmse = np.sqrt(mse)
            
            self.is_trained = True
            
            metrics = {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae)
            }
            
            logger.info(f"Training completed. Metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Generate predictions
        
        Args:
            data: Input data for prediction
            
        Returns:
            Numpy array of predictions
            
        Raises:
            RuntimeError: If model is not trained
            ValueError: If data is invalid
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
            
        if self.model is None:
            raise RuntimeError("Model not properly initialized")
        
        try:
            # Preprocess data
            processed_data = self.preprocess(data)
            
            # Make predictions
            predictions = self.model.predict(processed_data)
            
            if len(predictions) == 0:
                raise ValueError("No predictions generated")
            
            return predictions['yhat'].values
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            raise
    
    def save(self, path: str):
        """Save model to disk
        
        Args:
            path: Path to save model
            
        Raises:
            RuntimeError: If model is not initialized
        """
        if self.model is None:
            raise RuntimeError("Cannot save uninitialized model")
            
        try:
            joblib.dump(self.model, path)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def load(self, path: str):
        """Load model from disk
        
        Args:
            path: Path to load model from
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            RuntimeError: If model loading fails
        """
        try:
            self.model = joblib.load(path)
            self.is_trained = True
            logger.info(f"Model loaded from {path}")
        except FileNotFoundError:
            logger.error(f"Model file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise 