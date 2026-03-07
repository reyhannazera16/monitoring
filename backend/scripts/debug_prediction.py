
import os
import sys
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.database.db_manager import DatabaseManager
from backend.models.predictor import PredictionEngine
from backend.config import Config

def debug_prediction():
    db_manager = DatabaseManager(Config.DATABASE_PATH)
    engine = PredictionEngine(db_manager)
    location = 'Perkotaan'
    
    # Get training data
    readings = db_manager.get_readings_for_prediction(location=location, days=365)
    print(f"Training data points: {len(readings)}")
    
    # Train
    results = engine.train_models(location=location, training_days=365)
    
    # Generate
    periods = 10 # Just 10 for debugging
    
    # Load models if not already loaded (predictor.py does this)
    if location not in engine.co2_predictors:
        engine.load_models(location)
    
    co2_predictor = engine.co2_predictors[location]
    co2_predictions = co2_predictor.predict(periods, Config.CONFIDENCE_LEVEL)
    
    print(f"Prediction DataFrame length: {len(co2_predictions)}")
    print(co2_predictions.head())
    
    # Now check PredictionEngine.generate_predictions logic
    latest_reading = db_manager.get_latest_reading(location=location)
    last_date = pd.to_datetime(latest_reading['timestamp'])
    print(f"Last date: {last_date}")
    
    from backend.models.arima_model import generate_prediction_dates
    prediction_dates = generate_prediction_dates(last_date + pd.Timedelta(days=1), periods)
    print(f"Prediction dates length: {len(prediction_dates)}")
    
    co2_predictions['prediction_date'] = prediction_dates
    records = co2_predictions.to_dict('records')
    print(f"Records to insert: {len(records)}")
    
    count = db_manager.insert_predictions(records)
    print(f"Rows affected according to rowcount: {count}")
    
if __name__ == '__main__':
    debug_prediction()
