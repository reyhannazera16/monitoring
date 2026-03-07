"""
Database Manager for Air Quality Monitoring System
Handles all database operations including CRUD for sensor readings, predictions, and events
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os

class DatabaseManager:
    def __init__(self, db_path: str):
        """Initialize database connection"""
        self.db_path = db_path
        self._ensure_database_exists()
        
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        conn = self.get_connection()
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== SENSOR READINGS ====================
    
    def insert_sensor_reading(self, co2_ppm: float, co_ppm: float, 
                            mq7_detected: bool, location: str = 'Perkotaan', 
                            status: str = None, timestamp: datetime = None) -> int:
        """Insert a new sensor reading"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # Ensure standard Python types for SQLite compatibility
        # Use space instead of T for better consistency with SQLite default
        ts_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(timestamp, datetime) else str(timestamp)
        mq7_int = 1 if mq7_detected else 0
        
        cursor.execute('''
            INSERT INTO sensor_readings (timestamp, location, co2_ppm, co_ppm, mq7_detected, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ts_str, location, float(co2_ppm), float(co_ppm), mq7_int, status))
        
        reading_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reading_id
        
    def insert_sensor_readings_bulk(self, readings: List[Dict]):
        """Insert multiple sensor readings in a single transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            data_to_insert = []
            for r in readings:
                ts = r['timestamp']
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S') if isinstance(ts, datetime) else str(ts)
                mq7_int = 1 if r.get('mq7_detected', False) else 0
                data_to_insert.append((
                    ts_str,
                    r.get('location', 'Perkotaan'),
                    float(r['co2_ppm']),
                    float(r['co_ppm']),
                    mq7_int,
                    r.get('status')
                ))
            
            cursor.executemany('''
                INSERT INTO sensor_readings (timestamp, location, co2_ppm, co_ppm, mq7_detected, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
            
            conn.commit()
            print(f"Successfully inserted {len(readings)} records bulk.")
        except Exception as e:
            conn.rollback()
            print(f"Error in bulk insert: {e}")
            raise e
        finally:
            conn.close()
    
    def get_sensor_readings(self, location: str = None, 
                          start_date: datetime = None, 
                          end_date: datetime = None,
                          limit: int = None) -> List[Dict]:
        """Get sensor readings with optional location and date range filter"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM sensor_readings WHERE 1=1'
        params = []
        
        if location:
            query += ' AND location = ?'
            params.append(location)
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(start_date, datetime) else str(start_date))
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(end_date, datetime) else str(end_date))
        
        query += ' ORDER BY timestamp DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_latest_reading(self, location: str = 'Perkotaan') -> Optional[Dict]:
        """Get the most recent sensor reading for a specific location"""
        readings = self.get_sensor_readings(location=location, limit=1)
        return readings[0] if readings else None
    
    def get_readings_for_prediction(self, location: str = 'Perkotaan', days: int = 30) -> List[Dict]:
        """Get recent readings for model training for a specific location"""
        start_date = datetime.now() - timedelta(days=days)
        return self.get_sensor_readings(location=location, start_date=start_date)
    
    # ==================== PREDICTIONS ====================
    
    def insert_predictions(self, predictions: List[Dict]) -> int:
        """Insert multiple predictions using executemany for performance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            data_to_insert = []
            for pred in predictions:
                p_date = pred['prediction_date']
                p_date_str = p_date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(p_date, datetime) else str(p_date)
                
                data_to_insert.append((
                    p_date_str,
                    pred.get('location', 'Perkotaan'),
                    pred['parameter_type'],
                    float(pred['predicted_value']),
                    float(pred['confidence_lower']),
                    float(pred['confidence_upper']),
                    json.dumps(pred.get('model_params', {}))
                ))
            
            cursor.executemany('''
                INSERT INTO predictions 
                (prediction_date, location, parameter_type, predicted_value, 
                 confidence_lower, confidence_upper, model_params)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
            
            count = cursor.rowcount
            conn.commit()
            return count
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_predictions(self, parameter_type: str, 
                       location: str = 'Perkotaan',
                       start_date: datetime = None,
                       end_date: datetime = None) -> List[Dict]:
        """Get predictions for a specific parameter and location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM predictions 
            WHERE parameter_type = ? AND location = ?
        '''
        params = [parameter_type, location]
        
        if start_date:
            query += ' AND prediction_date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND prediction_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY prediction_date ASC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            data = dict(row)
            if data.get('model_params'):
                data['model_params'] = json.loads(data['model_params'])
            results.append(data)
        
        return results
    
    def clear_old_predictions(self, parameter_type: str, location: str = 'Perkotaan'):
        """Clear old predictions before inserting new ones"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM predictions WHERE parameter_type = ? AND location = ?', (parameter_type, location))
        conn.commit()
        conn.close()
    
    # ==================== EVENTS ====================
    
    def insert_event(self, event_type: str, parameter: str, 
                    severity: str, value: float, location: str = 'Perkotaan',
                    message: str = None, timestamp: datetime = None) -> int:
        """Insert an air quality event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if timestamp is None:
            timestamp = datetime.now()
        
        cursor.execute('''
            INSERT INTO air_quality_events 
            (timestamp, location, event_type, parameter, severity, value, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, location, event_type, parameter, severity, value, message))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    def get_events(self, location: str = 'Perkotaan',
                  start_date: datetime = None, 
                  end_date: datetime = None,
                  event_type: str = None) -> List[Dict]:
        """Get air quality events for a location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM air_quality_events WHERE location = ?'
        params = [location]
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        if event_type:
            query += ' AND event_type = ?'
            params.append(event_type)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== MODEL METADATA ====================
    
    def save_model_metadata(self, parameter_type: str, model_params: Dict,
                          aic: float, bic: float, training_samples: int,
                          location: str = 'Perkotaan'):
        """Save model training metadata for a location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Deactivate old models
        cursor.execute('''
            UPDATE model_metadata 
            SET is_active = 0 
            WHERE parameter_type = ? AND location = ?
        ''', (parameter_type, location))
        
        # Insert new model
        cursor.execute('''
            INSERT INTO model_metadata 
            (parameter_type, location, model_params, aic, bic, training_samples, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (parameter_type, location, json.dumps(model_params), aic, bic, training_samples))
        
        conn.commit()
        conn.close()
    
    def get_active_model_metadata(self, parameter_type: str, location: str = 'Perkotaan') -> Optional[Dict]:
        """Get active model metadata for a location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM model_metadata 
            WHERE parameter_type = ? AND location = ? AND is_active = 1
            ORDER BY trained_at DESC
            LIMIT 1
        ''', (parameter_type, location))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            data['model_params'] = json.loads(data['model_params'])
            return data
        return None
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self, location: str = 'Perkotaan',
                      start_date: datetime = None, 
                      end_date: datetime = None) -> Dict:
        """Get summary statistics for a location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                COUNT(*) as total_readings,
                AVG(co2_ppm) as avg_co2,
                MAX(co2_ppm) as max_co2,
                MIN(co2_ppm) as min_co2,
                AVG(co_ppm) as avg_co,
                MAX(co_ppm) as max_co,
                MIN(co_ppm) as min_co,
                SUM(CASE WHEN mq7_detected = 1 THEN 1 ELSE 0 END) as co_detections
            FROM sensor_readings
            WHERE location = ?
        '''
        params = [location]
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}
