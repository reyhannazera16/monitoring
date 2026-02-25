"""
Main Flask Application
Air Quality Prediction System
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from backend.api.routes import api
from backend.config import Config

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__,
                static_folder='../frontend',
                static_url_path='')
    
    # Configuration
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'Air Quality Prediction System'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("  AIR QUALITY PREDICTION SYSTEM")
    print("  ARIMA-based Air Quality Forecasting")
    print("="*60)
    print(f"\n  Server running on: http://localhost:5000")
    print(f"  API Documentation: http://localhost:5000/api")
    print(f"  Dashboard: http://localhost:5000")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
