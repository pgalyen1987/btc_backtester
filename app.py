from flask import Flask, render_template
import btc_chart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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