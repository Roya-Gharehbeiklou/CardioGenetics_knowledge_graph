import logging
from pathlib import Path
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv
import os
from src.api.routes import create_api_blueprint

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATA_DIR=Path(os.getenv('DATA_DIR', 'data')),
        VIZ_DIR=Path(os.getenv('VIZ_DIR', 'static/visualizations'))
    )
    
    # Ensure required directories exist
    app.config['DATA_DIR'].mkdir(parents=True, exist_ok=True)
    app.config['VIZ_DIR'].mkdir(parents=True, exist_ok=True)
    
    # Register routes
    api_bp = create_api_blueprint()
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        """Render the main application page"""
        return render_template('index.html')

    @app.route('/static/<path:path>')
    def send_static(path):
        """Serve static files"""
        return send_from_directory('static', path)

    return app

def main():
    """Main application entry point"""
    try:
        app = create_app()
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise

if __name__ == '__main__':
    main()