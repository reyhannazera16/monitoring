"""
ARIMA Model Implementation for Air Quality Prediction
Uses pmdarima for automatic parameter selection and statsmodels for forecasting
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
from typing import Tuple, Dict, List
import pickle
import os
from datetime import datetime, timedelta

class ARIMAPredictor:
    def __init__(self, max_p=5, max_d=2, max_q=5):
        """
        Initialize ARIMA predictor
        
        Args:
            max_p: Maximum AR order
            max_d: Maximum differencing order
            max_q: Maximum MA order
        """
        self.max_p = max_p
        self.max_d = max_d
        self.max_q = max_q
        self.model = None
        self.model_params = None
        self.aic = None
        self.bic = None
        
    def find_optimal_parameters(self, data: pd.Series) -> Tuple[int, int, int]:
        """
        Find optimal ARIMA parameters using auto_arima
        
        Args:
            data: Time series data
            
        Returns:
            Tuple of (p, d, q) parameters
        """
        print("Finding optimal ARIMA parameters...")
        
        # Use auto_arima to find best parameters
        model = auto_arima(
            data,
            start_p=0, max_p=self.max_p,
            start_d=0, max_d=self.max_d,
            start_q=0, max_q=self.max_q,
            seasonal=False,
            stepwise=True,
            suppress_warnings=True,
            error_action='ignore',
            trace=True
        )
        
        order = model.order
        self.aic = model.aic()
        self.bic = model.bic()
        
        print(f"Optimal parameters: p={order[0]}, d={order[1]}, q={order[2]}")
        print(f"AIC: {self.aic:.2f}, BIC: {self.bic:.2f}")
        
        return order
    
    def train(self, data: pd.Series, order: Tuple[int, int, int] = None) -> Dict:
        """
        Train ARIMA model
        
        Args:
            data: Time series data
            order: Optional (p, d, q) parameters. If None, will auto-select
            
        Returns:
            Dictionary with model metadata
        """
        # Find optimal parameters if not provided
        if order is None:
            order = self.find_optimal_parameters(data)
        
        # Train ARIMA model
        print(f"Training ARIMA{order} model...")
        self.model = ARIMA(data, order=order)
        self.model = self.model.fit()
        
        self.model_params = {
            'p': order[0],
            'd': order[1],
            'q': order[2]
        }
        
        self.aic = self.model.aic
        self.bic = self.model.bic
        
        print("Model training complete!")
        
        return {
            'params': self.model_params,
            'aic': self.aic,
            'bic': self.bic,
            'training_samples': len(data)
        }
    
    def predict(self, periods: int, confidence_level: float = 0.95) -> pd.DataFrame:
        """
        Generate predictions with confidence intervals
        
        Args:
            periods: Number of periods to forecast
            confidence_level: Confidence level for intervals (default 0.95)
            
        Returns:
            DataFrame with predictions and confidence intervals
        """
        if self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        # Generate forecast
        forecast_result = self.model.get_forecast(steps=periods)
        
        # Get predictions and confidence intervals
        predictions = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=1-confidence_level)
        
        # Create DataFrame
        df = pd.DataFrame({
            'predicted_value': predictions.values,
            'confidence_lower': conf_int.iloc[:, 0].values,
            'confidence_upper': conf_int.iloc[:, 1].values
        })
        
        return df
    
    def save_model(self, filepath: str):
        """Save trained model to file"""
        if self.model is None:
            raise ValueError("No model to save")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'params': self.model_params,
            'aic': self.aic,
            'bic': self.bic
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from file"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.model_params = model_data['params']
        self.aic = model_data['aic']
        self.bic = model_data['bic']
        
        print(f"Model loaded from {filepath}")
    
    def get_model_summary(self) -> str:
        """Get model summary"""
        if self.model is None:
            return "No model trained"
        
        return str(self.model.summary())


def prepare_time_series_data(readings: List[Dict], parameter: str) -> pd.Series:
    """
    Prepare time series data from sensor readings
    
    Args:
        readings: List of sensor reading dictionaries
        parameter: 'co2' or 'co'
        
    Returns:
        Pandas Series with datetime index
    """
    if not readings:
        raise ValueError("No data provided")
    
    # Convert to DataFrame
    df = pd.DataFrame(readings)
    
    # Convert timestamp to datetime - be explicit about format
    # Try multiple formats if needed, but the primary one is %Y-%m-%d %H:%M:%S
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Drop records with invalid timestamps
    df = df.dropna(subset=['timestamp'])
    
    if df.empty:
        raise ValueError("No valid data points after date parsing")
        
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)
    
    # Select parameter column
    column_map = {
        'co2': 'co2_ppm',
        'co': 'co_ppm'
    }
    
    if parameter not in column_map:
        raise ValueError(f"Invalid parameter: {parameter}")
    
    # Get the series
    series = df[column_map[parameter]]
    
    # Sort by index
    series = series.sort_index()
    
    # Resample to daily average (to reduce noise)
    series = series.resample('D').mean()
    
    # Forward fill missing values
    series = series.fillna(method='ffill')
    
    # Backward fill any remaining NaN at the start
    series = series.fillna(method='bfill')
    
    return series


def generate_prediction_dates(start_date: datetime, periods: int, freq: str = 'D') -> List[datetime]:
    """
    Generate prediction dates
    
    Args:
        start_date: Starting date
        periods: Number of periods
        freq: Frequency ('D' for daily, 'H' for hourly)
        
    Returns:
        List of datetime objects
    """
    dates = pd.date_range(start=start_date, periods=periods, freq=freq)
    return dates.to_pydatetime().tolist()
