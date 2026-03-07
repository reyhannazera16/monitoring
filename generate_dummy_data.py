"""
Generate realistic dummy air quality data with good visualization patterns
Data akan memiliki tren naik bertahap yang realistis untuk prediksi ARIMA
"""
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import os

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'data', 'air_quality.db')

def create_database():
    """Create database and tables using schema.sql"""
    print("📊 Menyiapkan database dengan schema baru...")
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Read schema file
    schema_path = os.path.join(PROJECT_ROOT, 'backend', 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables to ensure clean state
    cursor.execute('DROP TABLE IF EXISTS sensor_readings')
    cursor.execute('DROP TABLE IF EXISTS predictions')
    cursor.execute('DROP TABLE IF EXISTS air_quality_events')
    cursor.execute('DROP TABLE IF EXISTS model_metadata')
    
    # Execute schema
    cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    print("✅ Database dipicu ulang dengan schema terbaru!")

def generate_location_data(location, days=365):
    """
    Generate realistic data for a specific location
    """
    print(f"\n📈 Generating {days} days of data for {location}...")
    
    # Profiles
    profiles = {
        'Perkotaan': {
            'base_co2': 480,
            'trend_co2': 0.8,
            'daily_amp_co2': 60,
            'noise_co2': 20,
            'spike_chance': 0.1,
            'base_co': 2.5,
            'trend_co': 0.02
        },
        'Pedesaan': {
            'base_co2': 390,
            'trend_co2': 0.1,
            'daily_amp_co2': 25,
            'noise_co2': 10,
            'spike_chance': 0.02,
            'base_co': 1.0,
            'trend_co': 0.005
        }
    }
    
    prof = profiles.get(location, profiles['Perkotaan'])
    
    start_date = datetime.now() - timedelta(days=days)
    hours = days * 24
    timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
    
    data = []
    
    for i, ts in enumerate(timestamps):
        day_number = i / 24
        hour = ts.hour
        weekday = ts.weekday()
        
        # CO2
        trend = day_number * prof['trend_co2']
        daily = prof['daily_amp_co2'] * np.sin((hour - 6) * np.pi / 12) if 6 <= hour <= 18 else -prof['daily_amp_co2']/2
        weekly = 20 if weekday < 5 else -10
        seasonal = 20 * np.sin(day_number * 2 * np.pi / 120)
        noise = np.random.normal(0, prof['noise_co2'])
        spike = np.random.uniform(50, 200) if np.random.random() < prof['spike_chance'] else 0
        
        co2 = prof['base_co2'] + trend + daily + weekly + seasonal + noise + spike
        co2 = max(300, co2)
        
        # CO
        trend_co = day_number * prof['trend_co']
        daily_co = 2 * np.sin((hour - 6) * np.pi / 12) if 6 <= hour <= 18 else -0.5
        noise_co = np.random.normal(0, 0.4)
        spike_co = np.random.uniform(3, 10) if np.random.random() < (prof['spike_chance'] * 0.8) else 0
        
        co = prof['base_co'] + trend_co + daily_co + noise_co + spike_co
        co = max(0.1, co)
        
        mq7 = 1 if co > 9 else 0
        
        data.append((
            ts.strftime('%Y-%m-%d %H:%M:%S'),
            location,
            round(co2, 2),
            round(co, 2),
            mq7
        ))
    
    return data

def insert_data(data):
    """Insert data into database"""
    print(f"\n💾 Inserting {len(data)} records into database...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT INTO sensor_readings (timestamp, location, co2_ppm, co_ppm, mq7_detected)
        VALUES (?, ?, ?, ?, ?)
    ''', data)
    
    conn.commit()
    conn.close()

def main():
    print("="*70)
    print(" 🎯 MULTI-LOCATION DATA GENERATOR (Urban vs Rural)")
    print("="*70)
    
    create_database()
    
    # Generate data for both locations
    urban_data = generate_location_data('Perkotaan', days=365)
    insert_data(urban_data)
    
    rural_data = generate_location_data('Pedesaan', days=365)
    insert_data(rural_data)
    
    print("\n✅ SELESAI! Data dummy multi-lokasi telah dibuat.")
    print(f"📁 Database: {DATABASE_PATH}")
    print("="*70)

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
