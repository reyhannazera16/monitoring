import sys
import os

# Add the project root to the path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

app = create_app()

# This is required for Vercel to work with Flask
# Vercel looks for 'app' or 'application' in index.py
application = app
