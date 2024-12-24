"""
Web module for handling HTTP and WebSocket communication
"""

from .websocket import WebSocketClient
from .api import APIClient
from .handlers import register_handlers
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from ..data.data_loader import DataLoader
from ..visualization.chart_generator import ChartGenerator

app = Flask(__name__)
CORS(app)

@app.route('/api/historical-data', methods=['POST'])
def get_historical_data():
    try:
        data = request.get_json()
        period_days = data.get('period_days', 365)
        interval = data.get('interval', '1d')
        
        # Load historical data
        data_loader = DataLoader()
        df = data_loader.load_historical_data(period_days=period_days, interval=interval)
        
        # Generate chart
        chart_generator = ChartGenerator()
        chart_data = chart_generator.create_candlestick_chart(df)
        
        return jsonify({
            'success': True,
            'data': {
                'chart': chart_data,
                'timestamps': df.index.astype(str).tolist(),
                'prices': df['close'].tolist(),
                'volumes': df['volume'].tolist(),
                'open': df['open'].tolist(),
                'high': df['high'].tolist(),
                'low': df['low'].tolist(),
                'close': df['close'].tolist()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/technical-chart', methods=['POST'])
def get_technical_chart():
    try:
        data = request.get_json()
        period_days = data.get('period_days', 365)
        interval = data.get('interval', '1d')
        indicators = data.get('indicators', {})
        
        # Load historical data
        data_loader = DataLoader()
        df = data_loader.load_historical_data(period_days=period_days, interval=interval)
        
        # Calculate indicators
        indicator_data = {}
        for name, params in indicators.items():
            # Add indicator calculation logic here
            pass
        
        # Generate chart
        chart_generator = ChartGenerator()
        chart_data = chart_generator.create_technical_chart(df, indicator_data)
        
        return jsonify({
            'success': True,
            'data': {
                'chart': chart_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def create_app():
    return app

__all__ = ['WebSocketClient', 'APIClient', 'register_handlers'] 