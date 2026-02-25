"""
Standalone script to initialize database and generate sample data
Run this first before starting the server
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'data', 'air_quality.db')

def create_database():
    """Create database and tables"""
    print("Creating database...")
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            co2_ppm REAL NOT NULL,
            co_ppm REAL NOT NULL,
            mq7_detected BOOLEAN NOT NULL DEFAULT 0,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_date DATETIME NOT NULL,
            parameter_type TEXT NOT NULL,
            predicted_value REAL NOT NULL,
            confidence_lower REAL NOT NULL,
            confidence_upper REAL NOT NULL,
            model_params TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS air_quality_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            parameter TEXT NOT NULL,
            severity TEXT NOT NULL,
            value REAL NOT NULL,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parameter_type TEXT NOT NULL,
            model_params TEXT NOT NULL,
            aic REAL,
            bic REAL,
            training_samples INTEGER,
            trained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database created successfully!")

def generate_sample_data(days=365):
    """Generate sample air quality data"""
    print(f"\nGenerating {days} days of sample data...")
    
    start_date = datetime.now() - timedelta(days=days)
    timestamps = pd.date_range(start=start_date, periods=days*24, freq='H')
    
    data = []
    
    for i, ts in enumerate(timestamps):
        # Base values
        base_co2 = 350
        base_co = 2.5
        
        # Add upward trend
        trend_co2 = (i / len(timestamps)) * 0.6 * 800
        trend_co = (i / len(timestamps)) * 0.6 * 8
        
        # Add daily cycle
        hour = ts.hour
        daily_cycle_co2 = 50 * np.sin((hour - 6) * np.pi / 12)
        daily_cycle_co = 1.5 * np.sin((hour - 6) * np.pi / 12)
        
        # Add weekly cycle
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
        
        # MQ7 detection
        mq7_detected = 1 if (co_ppm > 8 and np.random.random() > 0.7) else 0
        
        data.append((
            ts.strftime('%Y-%m-%d %H:%M:%S'),
            round(co2_ppm, 2),
            round(co_ppm, 2),
            mq7_detected
        ))
    
    print(f"✓ Generated {len(data)} data points")
    return data

def insert_data(data):
    """Insert data into database"""
    print("\nInserting data into database...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT INTO sensor_readings (timestamp, co2_ppm, co_ppm, mq7_detected)
        VALUES (?, ?, ?, ?)
    ''', data)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Inserted {len(data)} records")

def main():
    print("="*60)
    print(" AIR QUALITY DATABASE SETUP")
    print("="*60)
    
    # Create database
    create_database()
    
    # Generate sample data
    data = generate_sample_data(days=365)
    
    # Insert data
    insert_data(data)
    
    # Show summary
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*), MIN(co2_ppm), MAX(co2_ppm), AVG(co2_ppm) FROM sensor_readings')
    count, min_co2, max_co2, avg_co2 = cursor.fetchone()
    
    cursor.execute('SELECT MIN(co_ppm), MAX(co_ppm), AVG(co_ppm) FROM sensor_readings')
    min_co, max_co, avg_co = cursor.fetchone()
    
    conn.close()
    
    print("\n" + "="*60)
    print(" DATA SUMMARY")
    print("="*60)
    print(f"Total records: {count}")
    print(f"CO₂ range: {min_co2:.2f} - {max_co2:.2f} ppm (avg: {avg_co2:.2f})")
    print(f"CO range: {min_co:.2f} - {max_co:.2f} ppm (avg: {avg_co:.2f})")
    print("\n✓ Setup complete! Database ready at:")
    print(f"  {DATABASE_PATH}")
    print("\nNext steps:")
    print("  1. Train models: python setup_models.py")
    print("  2. Start server: python backend/app.py")
    print("="*60)

if __name__ == '__main__':
    main()
