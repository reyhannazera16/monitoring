"""
Firebase Manager for Air Quality Monitoring System
Handles all database operations using Firebase Firestore
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseManager:
    def __init__(self):
        """Initialize Firebase connection"""
        self._initialize_firebase()
        try:
            self.db = firestore.client()
        except Exception as e:
            print(f"WARNING: Could not initialize Firestore client: {e}")
            self.db = None
        
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            # Check for credentials in environment variables (for Vercel)
            fb_creds_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
            
            if fb_creds_json:
                try:
                    cred_dict = json.loads(fb_creds_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                except Exception as e:
                    print(f"Error parsing FIREBASE_SERVICE_ACCOUNT: {e}")
                    raise e
            else:
                # Fallback to local file for development
                cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # If no credentials found, initialize without them if possible (will fail on actual DB calls)
                    # This prevents the app from crashing on startup if only doing static serving
                    print("WARNING: No Firebase credentials found. Database operations will fail.")
                    # In some environments, it might auto-initialize with ADC
                    try:
                        firebase_admin.initialize_app()
                    except:
                        pass

    # ==================== SENSOR READINGS ====================
    
    def insert_sensor_reading(self, co2_ppm: float, co_ppm: float, 
                            mq7_detected: bool, location: str = 'Perkotaan', 
                            status: str = None, timestamp: datetime = None) -> str:
        """Insert a new sensor reading into Firestore"""
        if timestamp is None:
            timestamp = datetime.now()
            
        data = {
            'timestamp': timestamp,
            'location': location,
            'co2_ppm': float(co2_ppm),
            'co_ppm': float(co_ppm),
            'mq7_detected': bool(mq7_detected),
            'status': status
        }
        
        _, doc_ref = self.db.collection('sensor_readings').add(data)
        return doc_ref.id
        
    def get_sensor_readings(self, location: str = None, 
                          start_date: datetime = None, 
                          end_date: datetime = None,
                          limit: int = None) -> List[Dict]:
        """Get sensor readings from Firestore"""
        query = self.db.collection('sensor_readings')
        
        if location:
            query = query.where('location', '==', location)
        
        if start_date:
            query = query.where('timestamp', '>=', start_date)
            
        if end_date:
            query = query.where('timestamp', '<=', end_date)
            
        query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)
        
        if limit:
            query = query.limit(limit)
            
        docs = query.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            # Convert Firestore timestamp to Python datetime string for API consistency
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            results.append(data)
            
        return results
    
    def get_latest_reading(self, location: str = 'Perkotaan') -> Optional[Dict]:
        """Get the most recent sensor reading"""
        readings = self.get_sensor_readings(location=location, limit=1)
        return readings[0] if readings else None
    
    # ==================== PREDICTIONS ====================
    
    def insert_predictions(self, predictions: List[Dict]) -> int:
        """Insert multiple predictions into Firestore using batch"""
        batch = self.db.batch()
        count = 0
        
        for pred in predictions:
            doc_ref = self.db.collection('predictions').document()
            
            data = {
                'prediction_date': pred['prediction_date'],
                'location': pred.get('location', 'Perkotaan'),
                'parameter_type': pred['parameter_type'],
                'predicted_value': float(pred['predicted_value']),
                'confidence_lower': float(pred['confidence_lower']),
                'confidence_upper': float(pred['confidence_upper']),
                'model_params': pred.get('model_params', {})
            }
            batch.set(doc_ref, data)
            count += 1
            
            # Firestore batch limit is 500
            if count % 500 == 0:
                batch.commit()
                batch = self.db.batch()
                
        batch.commit()
        return count
    
    def get_predictions(self, parameter_type: str, 
                       location: str = 'Perkotaan',
                       start_date: datetime = None,
                       end_date: datetime = None) -> List[Dict]:
        """Get predictions from Firestore"""
        query = self.db.collection('predictions')\
                        .where('parameter_type', '==', parameter_type)\
                        .where('location', '==', location)
        
        if start_date:
            query = query.where('prediction_date', '>=', start_date)
            
        if end_date:
            query = query.where('prediction_date', '<=', end_date)
            
        query = query.order_by('prediction_date', direction=firestore.Query.ASCENDING)
        
        docs = query.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            if 'prediction_date' in data:
                data['prediction_date'] = data['prediction_date'].strftime('%Y-%m-%d %H:%M:%S')
            results.append(data)
            
        return results
    
    def clear_old_predictions(self, parameter_type: str, location: str = 'Perkotaan'):
        """Clear old predictions from Firestore (Serverless functions may have timeout issues with large deletes)"""
        docs = self.db.collection('predictions')\
                       .where('parameter_type', '==', parameter_type)\
                       .where('location', '==', location)\
                       .stream()
        
        batch = self.db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            if count % 500 == 0:
                batch.commit()
                batch = self.db.batch()
        batch.commit()

    # ==================== EVENTS ====================
    
    def insert_event(self, event_type: str, parameter: str, 
                    severity: str, value: float, location: str = 'Perkotaan',
                    message: str = None, timestamp: datetime = None) -> str:
        """Insert an air quality event into Firestore"""
        if timestamp is None:
            timestamp = datetime.now()
            
        data = {
            'timestamp': timestamp,
            'location': location,
            'event_type': event_type,
            'parameter': parameter,
            'severity': severity,
            'value': float(value),
            'message': message
        }
        
        _, doc_ref = self.db.collection('air_quality_events').add(data)
        return doc_ref.id
    
    def get_events(self, location: str = 'Perkotaan',
                  start_date: datetime = None, 
                  end_date: datetime = None,
                  event_type: str = None) -> List[Dict]:
        """Get events from Firestore"""
        query = self.db.collection('air_quality_events').where('location', '==', location)
        
        if start_date:
            query = query.where('timestamp', '>=', start_date)
        if end_date:
            query = query.where('timestamp', '<=', end_date)
        if event_type:
            query = query.where('event_type', '==', event_type)
            
        query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)
        
        docs = query.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            results.append(data)
        return results

    # ==================== MODEL METADATA ====================
    
    def save_model_metadata(self, parameter_type: str, model_params: Dict,
                          aic: float, bic: float, training_samples: int,
                          location: str = 'Perkotaan'):
        """Save model metadata to Firestore"""
        # Deactivate old models
        docs = self.db.collection('model_metadata')\
                       .where('parameter_type', '==', parameter_type)\
                       .where('location', '==', location)\
                       .where('is_active', '==', True)\
                       .stream()
        
        for doc in docs:
            doc.reference.update({'is_active': False})
            
        # Insert new model
        data = {
            'parameter_type': parameter_type,
            'location': location,
            'model_params': model_params,
            'aic': float(aic),
            'bic': float(bic),
            'training_samples': int(training_samples),
            'is_active': True,
            'trained_at': datetime.now()
        }
        self.db.collection('model_metadata').add(data)
    
    def get_active_model_metadata(self, parameter_type: str, location: str = 'Perkotaan') -> Optional[Dict]:
        """Get active model metadata"""
        docs = self.db.collection('model_metadata')\
                       .where('parameter_type', '==', parameter_type)\
                       .where('location', '==', location)\
                       .where('is_active', '==', True)\
                       .order_by('trained_at', direction=firestore.Query.DESCENDING)\
                       .limit(1)\
                       .stream()
                       
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            if 'trained_at' in data:
                data['trained_at'] = data['trained_at'].strftime('%Y-%m-%d %H:%M:%S')
            return data
        return None

    # ==================== STATISTICS ====================
    
    def get_statistics(self, location: str = 'Perkotaan',
                      start_date: datetime = None, 
                      end_date: datetime = None) -> Dict:
        """Get summary statistics from Firestore (Note: Firestore AVG/SUM require separate calculations or extensions)"""
        # Simplified version: fetch readings and calculate
        # In production with large data, use Cloud Functions to maintain counters
        readings = self.get_sensor_readings(location=location, start_date=start_date, end_date=end_date)
        
        if not readings:
            return {}
            
        co2_vals = [r['co2_ppm'] for r in readings]
        co_vals = [r['co_ppm'] for r in readings]
        co_detections = sum(1 for r in readings if r.get('mq7_detected'))
        
        return {
            'total_readings': len(readings),
            'avg_co2': sum(co2_vals) / len(co2_vals),
            'max_co2': max(co2_vals),
            'min_co2': min(co2_vals),
            'avg_co': sum(co_vals) / len(co_vals),
            'max_co': max(co_vals),
            'min_co': min(co_vals),
            'co_detections': co_detections
        }
