"""Flask application factory"""

from flask import Flask
from flask_sock import Sock
import json
from datetime import datetime, timedelta
import random

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    sock = Sock(app)

    @sock.route('/data')
    def data(ws):
        """WebSocket endpoint for data"""
        while True:
            # Generate sample data
            data = {
                'type': 'data_update',
                'historical': [
                    {
                        'timestamp': (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                        'price': 42000 + random.uniform(-500, 500),
                        'volume': random.uniform(1, 100)
                    }
                    for i in range(24)
                ],
                'current': {
                    'price': 42000,
                    'volume': 100,
                    'high': 43000,
                    'low': 41000
                }
            }
            ws.send(json.dumps(data))
            ws.sleep(1)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 