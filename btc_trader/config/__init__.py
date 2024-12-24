"""Configuration package for application settings"""

import os

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Flask-Sock settings
    SOCK_SERVER_OPTIONS = {
        'ping_interval': 25,
        'ping_timeout': 120,
        'max_message_size': 65536
    }

__all__ = ['Config'] 