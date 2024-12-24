import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
DEBUG = True

# API settings
API_PREFIX = '/api'

# Backtesting settings
DEFAULT_SYMBOL = 'BTC-USD'
DEFAULT_PERIOD_DAYS = 365
DEFAULT_INTERVAL = '1d'
DEFAULT_INITIAL_CAPITAL = 10000.0
DEFAULT_STOP_LOSS = 0.02
DEFAULT_TAKE_PROFIT = 0.03
DEFAULT_POSITION_SIZE = 1.0
DEFAULT_COMMISSION = 0.001

# Cache settings
DATA_CACHE_SIZE = 10
RESULTS_CACHE_SIZE = 20

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'btc_trader.log'

# Strategy settings
AVAILABLE_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d']
MAX_PERIOD_DAYS = 1000 