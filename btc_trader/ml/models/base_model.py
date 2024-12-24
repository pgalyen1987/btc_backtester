"""Base model class for ML models"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

class BaseModel:
    """Base class for all ML models"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize base model
        
        Args:
            config: Model configuration dictionary
        """
        self.config = config or {}
        self.model = None
        self.is_trained = False
    
    def preprocess(self, data: pd.DataFrame) -> np.ndarray:
        """Preprocess data for model
        
        Args:
            data: Raw input data
            
        Returns:
            Preprocessed data ready for model
        """
        raise NotImplementedError
    
    def train(self, data: pd.DataFrame) -> Dict[str, float]:
        """Train model on data
        
        Args:
            data: Training data
            
        Returns:
            Dictionary of training metrics
        """
        raise NotImplementedError
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Generate predictions
        
        Args:
            data: Input data for prediction
            
        Returns:
            Model predictions
        """
        raise NotImplementedError
    
    def save(self, path: str):
        """Save model to disk
        
        Args:
            path: Path to save model
        """
        raise NotImplementedError
    
    def load(self, path: str):
        """Load model from disk
        
        Args:
            path: Path to load model from
        """
        raise NotImplementedError 