"""
Prediction Engine
Orchestrates ARIMA model training and prediction generation
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import os

from backend.models.arima_model import ARIMAPredictor, prepare_time_series_data, generate_prediction_dates
from backend.database.db_manager import DatabaseManager
from backend.config import Config

class PredictionEngine:
    """Main prediction engine for air quality forecasting"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize prediction engine"""
        self.db_manager = db_manager
        self.co2_predictors = {} # Dict of location -> predictor
        self.co_predictors = {}
        self.models_dir = os.path.join(Config.PROJECT_ROOT, 'data', 'models')
        os.makedirs(self.models_dir, exist_ok=True)
    
    def train_models(self, location: str = 'Perkotaan', training_days: int = 180) -> Dict:
        """
        Train ARIMA models for CO2 and CO for a specific location
        
        Args:
            location: The location to train for
            training_days: Number of days of historical data to use
        """
        print(f"=== Training ARIMA Models for {location} ===\n")
        
        # Get training data
        readings = self.db_manager.get_readings_for_prediction(location=location, days=training_days)
        
        if len(readings) < 30:
            raise ValueError(f"Insufficient data for training. Need at least 30 days, got {len(readings)} records")
        
        print(f"Using {len(readings)} records for training ({training_days} days)")
        
        results = {}
        
        # Train CO2 model
        print("\n--- Training CO2 Model ---")
        co2_series = prepare_time_series_data(readings, 'co2')
        co2_predictor = ARIMAPredictor(
            max_p=Config.ARIMA_PARAMS['max_p'],
            max_d=Config.ARIMA_PARAMS['max_d'],
            max_q=Config.ARIMA_PARAMS['max_q']
        )
        co2_metadata = co2_predictor.train(co2_series)
        
        # Save CO2 model
        co2_model_path = os.path.join(self.models_dir, f'co2_model_{location}.pkl')
        co2_predictor.save_model(co2_model_path)
        
        # Save metadata to database
        self.db_manager.save_model_metadata(
            parameter_type='co2',
            location=location,
            model_params=co2_metadata['params'],
            aic=co2_metadata['aic'],
            bic=co2_metadata['bic'],
            training_samples=co2_metadata['training_samples']
        )
        
        self.co2_predictors[location] = co2_predictor
        
        results['co2'] = co2_metadata
        
        # Train CO model
        print("\n--- Training CO Model ---")
        co_series = prepare_time_series_data(readings, 'co')
        co_predictor = ARIMAPredictor(
            max_p=Config.ARIMA_PARAMS['max_p'],
            max_d=Config.ARIMA_PARAMS['max_d'],
            max_q=Config.ARIMA_PARAMS['max_q']
        )
        co_metadata = co_predictor.train(co_series)
        
        # Save CO model
        co_model_path = os.path.join(self.models_dir, f'co_model_{location}.pkl')
        co_predictor.save_model(co_model_path)
        
        # Save metadata to database
        self.db_manager.save_model_metadata(
            parameter_type='co',
            location=location,
            model_params=co_metadata['params'],
            aic=co_metadata['aic'],
            bic=co_metadata['bic'],
            training_samples=co_metadata['training_samples']
        )
        
        self.co_predictors[location] = co_predictor
        
        results['co'] = co_metadata
        
        print("\nModel training complete!")
        
        return results
    
    def generate_predictions(self, location: str = 'Perkotaan', periods: int = None) -> Dict:
        """
        Generate predictions for CO2 and CO for a location
        
        Args:
            location: The location to predict for
            periods: Number of days to predict (default from config)
        """
        if periods is None:
            periods = Config.PREDICTION_PERIODS
        
        print(f"\n=== Generating {periods}-day Predictions for {location} ===\n")
        
        # Load models if not already loaded
        if location not in self.co2_predictors:
            self.load_models(location)
        
        # Get last reading date
        latest_reading = self.db_manager.get_latest_reading(location=location)
        if latest_reading:
            last_date = pd.to_datetime(latest_reading['timestamp'])
        else:
            last_date = datetime.now()
        
        start_date = last_date + timedelta(days=1)
        prediction_dates = generate_prediction_dates(start_date, periods)
        
        results = {}
        
        # Generate CO2 predictions
        print(f"Generating CO2 predictions for {location}...")
        co2_predictor = self.co2_predictors[location]
        co2_predictions = co2_predictor.predict(periods, Config.CONFIDENCE_LEVEL)
        co2_predictions['prediction_date'] = prediction_dates
        co2_predictions['parameter_type'] = 'co2'
        co2_predictions['location'] = location
        
        # Save to database
        self.db_manager.clear_old_predictions('co2', location=location)
        co2_records = co2_predictions.to_dict('records')
        self.db_manager.insert_predictions(co2_records)
        
        results['co2'] = co2_predictions
        
        # Generate CO predictions
        print(f"Generating CO predictions for {location}...")
        co_predictor = self.co_predictors[location]
        co_predictions = co_predictor.predict(periods, Config.CONFIDENCE_LEVEL)
        co_predictions['prediction_date'] = prediction_dates
        co_predictions['parameter_type'] = 'co'
        co_predictions['location'] = location
        
        # Save to database
        self.db_manager.clear_old_predictions('co', location=location)
        co_records = co_predictions.to_dict('records')
        self.db_manager.insert_predictions(co_records)
        
        results['co'] = co_predictions
        
        print("Predictions generated and saved!")
        
        return results
    
    def load_models(self, location: str = 'Perkotaan'):
        """Load trained models for a specific location from disk"""
        print(f"Loading trained models for {location}...")
        
        co2_model_path = os.path.join(self.models_dir, f'co2_model_{location}.pkl')
        co_model_path = os.path.join(self.models_dir, f'co_model_{location}.pkl')
        
        if not os.path.exists(co2_model_path) or not os.path.exists(co_model_path):
            raise FileNotFoundError(f"Models for {location} not found. Please train models first.")
        
        co2_p = ARIMAPredictor()
        co2_p.load_model(co2_model_path)
        self.co2_predictors[location] = co2_p
        
        co_p = ARIMAPredictor()
        co_p.load_model(co_model_path)
        self.co_predictors[location] = co_p
        
        print(f"Models for {location} loaded successfully!")
