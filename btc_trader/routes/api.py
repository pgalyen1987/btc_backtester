"""API routes for the application"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@api_bp.route('/market/current', methods=['GET'])
def get_current_market():
    """Get current market data"""
    market_data = {
        'price': 42000.0,
        'volume': 100.0,
        'high': 43000.0,
        'low': 41000.0
    }
    return jsonify(market_data)

@api_bp.route('/trades/latest', methods=['GET'])
def get_latest_trades():
    """Get latest trades"""
    trades_data = [
        {'price': 42000.0, 'amount': 1.0, 'side': 'buy'},
        {'price': 41900.0, 'amount': 0.5, 'side': 'sell'}
    ]
    return jsonify(trades_data)

@api_bp.route('/market/historical', methods=['GET'])
def get_historical_data():
    """Get historical market data for the last 24 hours"""
    # Generate 24 hours of sample data at 1-hour intervals
    data = []
    base_price = 42000.0
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    
    current_time = start_time
    while current_time <= end_time:
        # Generate a random price movement
        price_change = random.uniform(-500, 500)
        price = base_price + price_change
        
        data.append({
            'timestamp': current_time.isoformat(),
            'price': price,
            'volume': random.uniform(1, 100)
        })
        
        current_time += timedelta(hours=1)
        base_price = price  # Use the last price as base for next movement
    
    return jsonify(data) 