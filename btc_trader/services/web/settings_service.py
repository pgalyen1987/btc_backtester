from typing import Dict, Any
from flask import Flask
from .validation_service import ValidationService

class SettingsService:
    """Service for managing application settings"""
    
    def __init__(self, app: Flask):
        self.app = app
        
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings with defaults"""
        return {
            'apiKey': self.app.config.get('API_KEY', ''),
            'apiSecret': self.app.config.get('API_SECRET', ''),
            'defaultPeriodDays': self.app.config.get('DEFAULT_PERIOD_DAYS', 365),
            'defaultInterval': self.app.config.get('DEFAULT_INTERVAL', '1d'),
            'defaultInitialCapital': self.app.config.get('DEFAULT_INITIAL_CAPITAL', 10000),
            'defaultStopLoss': self.app.config.get('DEFAULT_STOP_LOSS', 0.02),
            'defaultTakeProfit': self.app.config.get('DEFAULT_TAKE_PROFIT', 0.03),
            'defaultPositionSize': self.app.config.get('DEFAULT_POSITION_SIZE', 1.0),
            'defaultCommission': self.app.config.get('DEFAULT_COMMISSION', 0.001),
            'enableRealTimeData': self.app.config.get('ENABLE_REAL_TIME_DATA', False),
            'enableNotifications': self.app.config.get('ENABLE_NOTIFICATIONS', False),
            'darkMode': self.app.config.get('DARK_MODE', False),
            'dataSource': self.app.config.get('DATA_SOURCE', 'yfinance'),
            'cacheTimeout': self.app.config.get('CACHE_TIMEOUT', 3600),
            'maxBacktestPeriod': self.app.config.get('MAX_BACKTEST_PERIOD', 1825),
        }
        
    def save_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save and validate settings"""
        if not data:
            raise ValueError('No data provided')
            
        # Validate settings
        validated_settings = ValidationService.validate_settings(data)
        
        # Update config
        for key, value in validated_settings.items():
            self.app.config[key.upper()] = value
            
        return validated_settings
        
    def reset_settings(self) -> Dict[str, Any]:
        """Reset settings to defaults"""
        self.app.config.from_object('config.default')
        return self.get_settings() 