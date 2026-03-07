"""
Standalone script to train ARIMA models
Run this after setup_database.py or generate_dummy_data.py
Ensures all values are converted to standard Python types for SQLite
"""
import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from backend.models.arima_model import ARIMAPredictor, prepare_time_series_data, generate_prediction_dates
from backend.config import Config

def get_all_readings():
    """Get all sensor readings from database"""
    db_path = Config.DATABASE_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sensor_readings ORDER BY timestamp ASC')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def save_predictions(predictions, parameter_type):
    """Save predictions to database with location support"""
    db_path = Config.DATABASE_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert new predictions
    for pred in predictions:
        location = pred.get('location', 'Perkotaan')
        
        # Clear old predictions for this specific location and parameter
        cursor.execute('DELETE FROM predictions WHERE parameter_type = ? AND location = ?', (parameter_type, location))
        
        p_date = pred['prediction_date']
        if hasattr(p_date, 'to_pydatetime'):
            p_date = p_date.to_pydatetime()
        elif isinstance(p_date, str):
            p_date = datetime.strptime(p_date, '%Y-%m-%d %H:%M:%S')

        date_str = p_date.strftime('%Y-%m-%d %H:%M:%S')
            
        cursor.execute('''
            INSERT INTO predictions 
            (prediction_date, location, parameter_type, predicted_value, confidence_lower, confidence_upper)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            date_str,
            location,
            parameter_type,
            float(pred['predicted_value']),
            float(pred['confidence_lower']),
            float(pred['confidence_upper'])
        ))
    
    conn.commit()
    conn.close()

def save_model_metadata(parameter_type, params, aic, bic, training_samples, location='Perkotaan'):
    """Save model metadata to database with location support"""
    db_path = Config.DATABASE_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Deactivate old models for this location and parameter
    cursor.execute('UPDATE model_metadata SET is_active = 0 WHERE parameter_type = ? AND location = ?', (parameter_type, location))
    
    # Convert parameters to standard python types
    clean_params = {k: int(v) if hasattr(v, 'item') else v for k, v in params.items()}
    
    # Insert new model
    cursor.execute('''
        INSERT INTO model_metadata 
        (parameter_type, location, model_params, aic, bic, training_samples, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (
        parameter_type, 
        location,
        json.dumps(clean_params), 
        float(aic), 
        float(bic), 
        int(training_samples)
    ))
    
    conn.commit()
    conn.close()

def main():
    print("="*60)
    print(" 🚀 MULTI-LOCATION ARIMA MODEL TRAINING")
    print("="*60)
    
    locations = ['Perkotaan', 'Pedesaan']
    
    try:
        for location in locations:
            print(f"\n" + "#"*60)
            print(f" 📍 PROCESSING LOCATION: {location}")
            print("#" * 60)
            
            # Get readings for this location
            # Note: simplified for this script, we'll fetch all filter by location
            db_path = Config.DATABASE_PATH
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sensor_readings WHERE location = ? ORDER BY timestamp ASC', (location,))
            readings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            print(f"✓ Loaded {len(readings)} records for {location}")
            
            if len(readings) < 100:
                print(f"✗ Skipping {location}: Insufficient data.")
                continue
            
            # Prepare data
            co2_series = prepare_time_series_data(readings, 'co2')
            co_series = prepare_time_series_data(readings, 'co')
            
            # Train and Save CO2
            print(f"\n--- Training CO2 Model ({location}) ---")
            co2_pred = ARIMAPredictor(max_p=5, max_d=2, max_q=5)
            co2_meta = co2_pred.train(co2_series)
            
            models_dir = os.path.join(PROJECT_ROOT, 'data', 'models')
            os.makedirs(models_dir, exist_ok=True)
            co2_pred.save_model(os.path.join(models_dir, f'co2_model_{location}.pkl'))
            save_model_metadata('co2', co2_meta['params'], co2_meta['aic'], co2_meta['bic'], co2_meta['training_samples'], location)
            
            # Train and Save CO
            print(f"\n--- Training CO Model ({location}) ---")
            co_pred = ARIMAPredictor(max_p=5, max_d=2, max_q=5)
            co_meta = co_pred.train(co_series)
            
            co_pred.save_model(os.path.join(models_dir, f'co_model_{location}.pkl'))
            save_model_metadata('co', co_meta['params'], co_meta['aic'], co_meta['bic'], co_meta['training_samples'], location)
            
            # Predictions
            periods = 365
            last_date = pd.to_datetime(readings[-1]['timestamp'])
            start_date = last_date + timedelta(days=1)
            prediction_dates = generate_prediction_dates(start_date, periods)
            
            print(f"\nGenerating 365-day predictions for {location}...")
            
            # CO2 Predictions
            co2_preds_df = co2_pred.predict(periods, 0.95)
            co2_preds_df['prediction_date'] = prediction_dates
            co2_preds_data = co2_preds_df.to_dict('records')
            for p in co2_preds_data: p['location'] = location
            save_predictions(co2_preds_data, 'co2')
            
            # CO Predictions
            co_preds_df = co_pred.predict(periods, 0.95)
            co_preds_df['prediction_date'] = prediction_dates
            co_preds_data = co_preds_df.to_dict('records')
            for p in co_preds_data: p['location'] = location
            save_predictions(co_preds_data, 'co')
            
            print(f"✓ {location} tasks complete!")
            
        print("\n" + "="*60)
        print(" ✅ ALL LOCATIONS TRAINED SUCCESSFULLY!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
