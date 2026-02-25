"""
Sample Data Generator for Testing
Generates realistic air quality data with trends and patterns
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from config import Config

class SampleDataGenerator:
    """Generate realistic sample air quality data"""
    
    @staticmethod
    def generate_historical_data(location: str = 'Perkotaan',
                                days: int = 365, 
                                start_date: datetime = None,
                                trend_factor: float = 0.5) -> pd.DataFrame:
        """
        Generate historical sensor data with realistic patterns
        
        Args:
            days: Number of days of data to generate
            start_date: Starting date (default: 1 year ago)
            trend_factor: Upward trend strength (0-1)
            
        Returns:
            DataFrame with generated data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=days)
        
        # Generate timestamps (every 2 seconds, then aggregate to hourly)
        timestamps = pd.date_range(start=start_date, periods=days*24, freq='H')
        
        data = []
        
        for i, ts in enumerate(timestamps):
            # Base values
            base_co2 = 350
            base_co = 2.5
            
            # Add upward trend (simulating industrial pollution increase)
            trend_co2 = (i / len(timestamps)) * trend_factor * 800
            trend_co = (i / len(timestamps)) * trend_factor * 8
            
            # Add daily cycle (higher during day, lower at night)
            hour = ts.hour
            daily_cycle_co2 = 50 * np.sin((hour - 6) * np.pi / 12)
            daily_cycle_co = 1.5 * np.sin((hour - 6) * np.pi / 12)
            
            # Add weekly cycle (higher on weekdays)
            weekday = ts.weekday()
            weekly_cycle_co2 = 30 if weekday < 5 else -20
            weekly_cycle_co = 1.0 if weekday < 5 else -0.5
            
            # Add random noise
            noise_co2 = np.random.normal(0, 20)
            noise_co = np.random.normal(0, 0.5)
            
            # Calculate final values
            co2_ppm = base_co2 + trend_co2 + daily_cycle_co2 + weekly_cycle_co2 + noise_co2
            co_ppm = base_co + trend_co + daily_cycle_co + weekly_cycle_co + noise_co
            
            # Ensure non-negative
            co2_ppm = max(0, co2_ppm)
            co_ppm = max(0, co_ppm)
            
            # MQ7 detection (random, more likely when CO is high)
            mq7_detected = co_ppm > 8 and np.random.random() > 0.7
            
            data.append({
                'timestamp': ts.to_pydatetime(),
                'location': location,
                'co2_ppm': float(round(co2_ppm, 2)),
                'co_ppm': float(round(co_ppm, 2)),
                'mq7_detected': bool(mq7_detected)
            })
        
        df = pd.DataFrame(data)
        return df
    
    @staticmethod
    def save_to_csv(df: pd.DataFrame, filepath: str):
        """Save data to CSV file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
    
    @staticmethod
    def save_to_database(df: pd.DataFrame, db_manager: DatabaseManager):
        """Save data to database using bulk insert"""
        print(f"Preparing {len(df)} records for bulk insertion...")
        readings = df.to_dict('records')
        db_manager.insert_sensor_readings_bulk(readings)
        print("Data insertion complete!")


def main():
    """Generate and save sample data"""
    print("=== Air Quality Sample Data Generator ===\n")
    
    # Generate Perkotaan data
    print("Generating 12 months (Perkotaan)...")
    df_urban = SampleDataGenerator.generate_historical_data(
        location='Perkotaan',
        days=365,
        trend_factor=0.6
    )
    
    # Generate Pedesaan data (lower levels, lower trend)
    print("Generating 12 months (Pedesaan)...")
    df_rural = SampleDataGenerator.generate_historical_data(
        location='Pedesaan',
        days=365,
        trend_factor=0.3
    )
    
    # Save to database
    db_manager = DatabaseManager(Config.DATABASE_PATH)
    SampleDataGenerator.save_to_database(df_urban, db_manager)
    SampleDataGenerator.save_to_database(df_rural, db_manager)
    
    print("\n✓ Sample data generation complete for both locations!")


if __name__ == '__main__':
    main()
