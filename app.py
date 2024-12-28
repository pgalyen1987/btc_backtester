from flask import Flask, render_template, send_from_directory, make_response
import btc_chart
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(SCRIPT_DIR, 'static')
template_folder = os.path.join(SCRIPT_DIR, 'templates')

# Create template directory if it doesn't exist
os.makedirs(template_folder, exist_ok=True)

app = Flask(__name__, 
           static_folder=static_folder,
           template_folder=template_folder)

@app.route('/favicon.ico')
def favicon():
    response = make_response(send_from_directory(
        os.path.join(app.root_path, 'static', 'img'),
        'favicon.ico',
        mimetype='image/x-icon'
    ))
    # Set headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/')
def dashboard() -> str:
    logger.info("Dashboard route accessed")
    try:
        btc_chart.main()
        logger.info("BTC chart generated successfully")
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error in dashboard route: {e}")
        raise

@app.route('/static/<path:filename>')
def serve_static(filename):
    response = make_response(send_from_directory(app.static_folder, filename))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False) 