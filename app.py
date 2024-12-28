from flask import Flask, render_template
import btc_chart
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(SCRIPT_DIR, 'static')

app = Flask(__name__, static_folder=static_folder)

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

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False) 