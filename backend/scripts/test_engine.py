
import os
import sys
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.database.db_manager import DatabaseManager
from backend.models.predictor import PredictionEngine
from backend.config import Config

def test_engine():
    db_manager = DatabaseManager(Config.DATABASE_PATH)
    engine = PredictionEngine(db_manager)
    location = 'Perkotaan'
    
    # Check readings
    readings = db_manager.get_readings_for_prediction(location=location, days=365)
    print(f"Readings found: {len(readings)}")
    
    # Train
    engine.train_models(location=location, training_days=30) # Use 30 for speed
    
    # Generate
    results = engine.generate_predictions(location=location, periods=10)
    
    co2_df = results['co2']
    print(f"CO2 Prediction DataFrame Length: {len(co2_df)}")
    print(f"Columns: {co2_df.columns.tolist()}")
    
    # Verify records in DB
    rows = db_manager.get_predictions('co2', location=location)
    print(f"Predictions found in DB for co2: {len(rows)}")

if __name__ == '__main__':
    test_engine()
