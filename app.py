from flask import Flask, render_template, send_from_directory, make_response, request, jsonify, Response
from flask_cors import CORS
import btc_chart
import logging
import os
from datetime import datetime
import traceback

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    # Get the directory where the script is located
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(SCRIPT_DIR, 'static')
    template_folder = os.path.join(SCRIPT_DIR, 'templates')

    # Create necessary directories
    os.makedirs(static_folder, exist_ok=True)
    os.makedirs(template_folder, exist_ok=True)
    os.makedirs(os.path.join(static_folder, 'img'), exist_ok=True)

    # Initialize Flask app
    app = Flask(__name__, 
               static_folder=static_folder,
               template_folder=template_folder)

    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Error handler for all exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }), 500

    @app.route('/installHook.js.map', methods=['GET'])
    def handle_install_hook_map():
        """Handle installHook.js.map requests."""
        logger.info("Handling installHook.js.map request")
        response = make_response('{"version":3,"file":"installHook.js","mappings":"","sources":[],"names":[]}')
        response.headers.update({
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Access-Control-Allow-Origin': '*'
        })
        return response

    @app.route('/favicon.ico')
    def favicon():
        try:
            response = make_response(send_from_directory(
                os.path.join(app.root_path, 'static', 'img'),
                'favicon.ico',
                mimetype='image/x-icon'
            ))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            return response
        except Exception as e:
            logger.error(f"Error serving favicon: {e}")
            return Response(status=404)

    @app.route('/')
    def dashboard():
        logger.info("Dashboard route accessed")
        try:
            btc_chart.main()
            logger.info("BTC chart generated successfully")
            return render_template('dashboard.html')
        except Exception as e:
            logger.error(f"Error in dashboard route: {e}")
            logger.error(traceback.format_exc())
            raise

    @app.route('/update_chart', methods=['POST', 'OPTIONS'])
    def update_chart():
        logger.info(f"Update chart route accessed with method: {request.method}")
        
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            return response

        try:
            # Log the raw request data
            logger.info(f"Request headers: {dict(request.headers)}")
            logger.info(f"Request data: {request.get_data(as_text=True)}")

            data = request.get_json(force=True)
            if not data:
                logger.error("No JSON data received")
                return jsonify({"status": "error", "message": "No data provided"}), 400

            logger.info(f"Received data: {data}")

            interval = data.get('interval', '1d')
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            if not start_date:
                return jsonify({"status": "error", "message": "Start date is required"}), 400

            logger.info(f"Processing update with interval={interval}, start_date={start_date}, end_date={end_date}")
            
            # Convert end_date to datetime for validation
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            
            # Validate date range
            if start_datetime > end_datetime:
                return jsonify({"status": "error", "message": "Start date cannot be after end date"}), 400
            
            # Get BTC data with specified parameters
            btc_data = btc_chart.get_btc_data(start=start_date, end=end_date, interval=interval)
            
            # Create and save the chart
            btc_chart.create_interactive_chart(btc_data)
            
            response_data = {
                "status": "success",
                "data": {
                    "interval": interval,
                    "start_date": start_date,
                    "end_date": end_date,
                    "points": len(btc_data)
                }
            }
            logger.info(f"Chart updated successfully. Response: {response_data}")
            return jsonify(response_data)

        except ValueError as ve:
            logger.error(f"Invalid date format: {ve}")
            logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": f"Invalid date format: {str(ve)}"}), 400
        except Exception as e:
            logger.error(f"Error updating chart: {e}")
            logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/<path:filename>.map')
    def handle_source_maps(filename):
        """Handle all other source map requests."""
        response = make_response('{"version": 3, "sources": [], "mappings": ""}')
        response.headers['Content-Type'] = 'application/json'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @app.route('/%3Canonymous%20code%3E')
    def handle_anonymous_code():
        """Handle anonymous code requests."""
        response = make_response('{}')
        response.headers['Content-Type'] = 'application/json'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        try:
            response = make_response(send_from_directory(app.static_folder, filename))
            # Set proper MIME type for CSS files
            if filename.endswith('.css'):
                response.headers['Content-Type'] = 'text/css; charset=utf-8'
            response.headers.update({
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Last-Modified': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'Vary': 'Accept-Encoding'
            })
            return response
        except Exception as e:
            logger.error(f"Error serving static file {filename}: {e}")
            return Response(status=404)

    return app

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False) 