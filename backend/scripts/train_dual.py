
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.database.db_manager import DatabaseManager
from backend.models.predictor import PredictionEngine
from backend.config import Config

def train_all():
    db_manager = DatabaseManager(Config.DATABASE_PATH)
    engine = PredictionEngine(db_manager)
    
    locations = ['Perkotaan', 'Pedesaan']
    
    for loc in locations:
        print(f"\nTraining models for {loc}...")
        try:
            results = engine.train_models(location=loc, training_days=365)
            print(f"Training successful for {loc}")
            
            print(f"Generating predictions for {loc}...")
            engine.generate_predictions(location=loc, periods=Config.PREDICTION_PERIODS)
            print(f"Predictions generated for {loc}")
        except Exception as e:
            print(f"Error training {loc}: {e}")

if __name__ == '__main__':
    print("Starting dual location training process...")
    train_all()
    print("Dual location training process finished.")
