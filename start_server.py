"""
Simple script to train models and start server
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Just start the server - it will train models on first request if needed
print("="*70)
print(" 🚀 STARTING AIR QUALITY PREDICTION SERVER")
print("="*70)
print("\nServer will start on: http://localhost:5000")
print("\nPress CTRL+C to stop the server")
print("="*70)

# Import and run Flask app
from backend.app import create_app

app = create_app()
app.run(host='0.0.0.0', port=5000, debug=True)
