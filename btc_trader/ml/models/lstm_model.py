"""LSTM model for time series prediction"""

from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from .base_model import BaseModel

class LSTMModel(BaseModel):
    """LSTM model for time series prediction"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize LSTM model
        
        Args:
            config: Model configuration dictionary with parameters:
                - sequence_length: Length of input sequences
                - n_features: Number of input features
                - n_units: List of LSTM units per layer
                - dropout: Dropout rate
                - learning_rate: Learning rate for optimizer
        """
        super().__init__(config)
        self.sequence_length = config.get('sequence_length', 60)
        self.n_features = config.get('n_features', 1)
        self.n_units = config.get('n_units', [64, 32])
        self.dropout = config.get('dropout', 0.2)
        self.learning_rate = config.get('learning_rate', 0.001)
        
        if not self.model:
            self._build_model()
    
    def _build_model(self):
        """Build LSTM model architecture"""
        self.model = Sequential()
        
        # Add LSTM layers
        for i, units in enumerate(self.n_units):
            if i == 0:
                self.model.add(LSTM(
                    units=units,
                    return_sequences=i < len(self.n_units) - 1,
                    input_shape=(self.sequence_length, self.n_features)
                ))
            else:
                self.model.add(LSTM(
                    units=units,
                    return_sequences=i < len(self.n_units) - 1
                ))
            
            # Add dropout after each LSTM layer
            self.model.add(Dropout(self.dropout))
        
        # Add output layer
        self.model.add(Dense(1))
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM input
        
        Args:
            data: Input data array
            
        Returns:
            Tuple of (X, y) arrays
        """
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def preprocess(self, data: pd.DataFrame) -> np.ndarray:
        """Preprocess data for LSTM model
        
        Args:
            data: DataFrame with features
            
        Returns:
            Preprocessed numpy array
        """
        # Convert to numpy and normalize
        data_array = data.values
        data_mean = data_array.mean()
        data_std = data_array.std()
        normalized = (data_array - data_mean) / data_std
        
        return normalized
    
    def train(self, data: pd.DataFrame, 
             validation_split: float = 0.2,
             epochs: int = 100,
             batch_size: int = 32) -> Dict[str, float]:
        """Train LSTM model
        
        Args:
            data: Training data
            validation_split: Fraction of data to use for validation
            epochs: Number of training epochs
            batch_size: Training batch size
            
        Returns:
            Dictionary of training metrics
        """
        # Preprocess data
        processed_data = self.preprocess(data)
        
        # Create sequences
        X, y = self._create_sequences(processed_data)
        
        # Train model
        history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            verbose=0
        )
        
        self.is_trained = True
        
        # Return last epoch metrics
        return {
            'loss': history.history['loss'][-1],
            'val_loss': history.history['val_loss'][-1],
            'mae': history.history['mae'][-1],
            'val_mae': history.history['val_mae'][-1]
        }
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Generate predictions
        
        Args:
            data: Input data for prediction
            
        Returns:
            Numpy array of predictions
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        # Preprocess data
        processed_data = self.preprocess(data)
        
        # Create sequences
        X, _ = self._create_sequences(processed_data)
        
        # Generate predictions
        predictions = self.model.predict(X)
        
        return predictions.squeeze()
    
    def save(self, path: str):
        """Save model to disk
        
        Args:
            path: Path to save model
        """
        self.model.save(path)
    
    def load(self, path: str):
        """Load model from disk
        
        Args:
            path: Path to load model from
        """
        self.model = load_model(path)
        self.is_trained = True 