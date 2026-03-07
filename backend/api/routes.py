"""
Flask API Routes for Air Quality Monitoring System
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import pandas as pd
import os

from backend.database.firebase_manager import FirebaseManager
from backend.models.predictor import PredictionEngine
from backend.utils.air_quality_standards import AirQualityStandards
from backend.utils.survival_calculator import SurvivalCalculator
from backend.config import Config

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Initialize Firebase manager
db_manager = FirebaseManager()

# ==================== DATA LOGGING ====================

@api.route('/log', methods=['POST'])
def log_sensor_data():
    """Log sensor data from Arduino"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['co2_ppm', 'co_ppm']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract data
        co2_ppm = float(data['co2_ppm'])
        co_ppm = float(data['co_ppm'])
        mq7_detected = data.get('mq7_detected', False)
        location = data.get('location', 'Perkotaan')
        timestamp_str = data.get('timestamp')
        
        # Parse timestamp
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()
        
        # Classify air quality
        co2_class = AirQualityStandards.classify_co2(co2_ppm)
        co_class = AirQualityStandards.classify_co(co_ppm)
        
        # Determine overall status
        if co2_class['category'] in ['sangat_tidak_sehat', 'berbahaya'] or \
           co_class['category'] in ['sangat_tidak_sehat', 'berbahaya']:
            status = 'danger'
        elif co2_class['category'] == 'tidak_sehat' or co_class['category'] == 'tidak_sehat':
            status = 'warning'
        else:
            status = 'good'
        
        # Insert into database
        reading_id = db_manager.insert_sensor_reading(
            co2_ppm=co2_ppm,
            co_ppm=co_ppm,
            mq7_detected=mq7_detected,
            location=location,
            status=status,
            timestamp=timestamp
        )
        
        # Log event if threshold crossed
        if status in ['warning', 'danger']:
            if co2_class['category'] in ['tidak_sehat', 'sangat_tidak_sehat', 'berbahaya']:
                db_manager.insert_event(
                    event_type='threshold_crossed',
                    parameter='co2',
                    severity=co2_class['category'],
                    value=co2_ppm,
                    message=f"CO2 level reached {co2_class['label']}: {co2_ppm:.2f} ppm",
                    timestamp=timestamp
                )
            
            if co_class['category'] in ['tidak_sehat', 'sangat_tidak_sehat', 'berbahaya']:
                db_manager.insert_event(
                    event_type='threshold_crossed',
                    parameter='co',
                    severity=co_class['category'],
                    value=co_ppm,
                    message=f"CO level reached {co_class['label']}: {co_ppm:.2f} ppm",
                    timestamp=timestamp
                )
        
        return jsonify({
            'success': True,
            'reading_id': reading_id,
            'status': status,
            'co2_classification': co2_class,
            'co_classification': co_class
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== DATA RETRIEVAL ====================

@api.route('/data/historical', methods=['GET'])
def get_historical_data():
    """Get historical sensor data"""
    try:
        # Get query parameters
        location = request.args.get('location', 'Perkotaan')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        # Parse dates
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        # Get data
        readings = db_manager.get_sensor_readings(
            location=location,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        # Add classifications
        for reading in readings:
            reading['co2_classification'] = AirQualityStandards.classify_co2(reading['co2_ppm'])
            reading['co_classification'] = AirQualityStandards.classify_co(reading['co_ppm'])
        
        return jsonify({
            'success': True,
            'count': len(readings),
            'data': readings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/data/latest', methods=['GET'])
def get_latest_data():
    """Get latest sensor reading"""
    try:
        location = request.args.get('location', 'Perkotaan')
        reading = db_manager.get_latest_reading(location=location)
        
        if reading:
            reading['co2_classification'] = AirQualityStandards.classify_co2(reading['co2_ppm'])
            reading['co_classification'] = AirQualityStandards.classify_co(reading['co_ppm'])
        
        return jsonify({
            'success': True,
            'data': reading
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PREDICTIONS ====================

@api.route('/predictions/<parameter>', methods=['GET'])
def get_predictions(parameter):
    """Get predictions for CO2 or CO"""
    try:
        if parameter not in ['co2', 'co']:
            return jsonify({'error': 'Invalid parameter. Use co2 or co'}), 400
        
        # Get query parameters
        location = request.args.get('location', 'Perkotaan')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        # Get predictions
        predictions = db_manager.get_predictions(
            parameter_type=parameter,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add classifications
        for pred in predictions:
            if parameter == 'co2':
                pred['classification'] = AirQualityStandards.classify_co2(pred['predicted_value'])
            else:
                pred['classification'] = AirQualityStandards.classify_co(pred['predicted_value'])
        
        # Get model metadata
        model_metadata = db_manager.get_active_model_metadata(parameter, location=location)
        
        return jsonify({
            'success': True,
            'parameter': parameter,
            'count': len(predictions),
            'model_metadata': model_metadata,
            'data': predictions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ANALYSIS ====================

@api.route('/analysis/survival', methods=['GET'])
def get_survival_analysis():
    """Get survival time analysis"""
    try:
        location = request.args.get('location', 'Perkotaan')
        # Get predictions
        co2_predictions = db_manager.get_predictions('co2', location=location)
        co_predictions = db_manager.get_predictions('co', location=location)
        
        if not co2_predictions or not co_predictions:
            return jsonify({'error': 'No predictions available. Please train models first.'}), 404
        
        # Convert to DataFrames
        co2_df = pd.DataFrame(co2_predictions)
        co2_df['prediction_date'] = pd.to_datetime(co2_df['prediction_date'])
        
        co_df = pd.DataFrame(co_predictions)
        co_df['prediction_date'] = pd.to_datetime(co_df['prediction_date'])
        
        # Calculate survival time
        analysis = SurvivalCalculator.calculate_survival_time(co2_df, co_df)
        
        # Add best/worst scenarios
        co2_scenarios = SurvivalCalculator.calculate_best_worst_scenarios(co2_df, 'co2')
        co_scenarios = SurvivalCalculator.calculate_best_worst_scenarios(co_df, 'co')
        
        analysis['scenarios'] = {
            'co2': co2_scenarios,
            'co': co_scenarios
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== STATISTICS ====================

@api.route('/statistics', methods=['GET'])
def get_statistics():
    """Get summary statistics"""
    try:
        # Get query parameters
        location = request.args.get('location', 'Perkotaan')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        # Get statistics
        stats = db_manager.get_statistics(location=location, start_date=start_date, end_date=end_date)
        
        # Add classifications for averages
        if stats.get('avg_co2'):
            stats['avg_co2_classification'] = AirQualityStandards.classify_co2(stats['avg_co2'])
        if stats.get('avg_co'):
            stats['avg_co_classification'] = AirQualityStandards.classify_co(stats['avg_co'])
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== MODEL MANAGEMENT ====================

@api.route('/model/train', methods=['POST'])
def train_models():
    """Train ARIMA models"""
    try:
        data = request.get_json() or {}
        training_days = data.get('training_days', 180)
        prediction_periods = data.get('prediction_periods', Config.PREDICTION_PERIODS)
        
        # Initialize prediction engine
        engine = PredictionEngine(db_manager)
        
        # Train models for a specific location
        location = data.get('location', 'Perkotaan')
        training_results = engine.train_models(location=location, training_days=training_days)
        
        # Generate predictions
        prediction_results = engine.generate_predictions(location=location, periods=prediction_periods)
        
        return jsonify({
            'success': True,
            'training_results': training_results,
            'prediction_count': {
                'co2': len(prediction_results['co2']),
                'co': len(prediction_results['co'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== EXPORT ====================

@api.route('/export/csv', methods=['GET'])
def export_csv():
    """Export data as CSV"""
    try:
        # Get query parameters
        location = request.args.get('location', 'Perkotaan')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        # Get data
        readings = db_manager.get_sensor_readings(
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(readings)
        
        # Map location labels for display
        location_labels = {'Perkotaan': 'Permukiman Industri'}
        if 'location' in df.columns:
            df['location'] = df['location'].replace(location_labels)
        
        # Save to CSV
        export_path = os.path.join(Config.EXPORT_DIR, f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        os.makedirs(Config.EXPORT_DIR, exist_ok=True)
        df.to_csv(export_path, index=False)
        
        return send_file(export_path, as_attachment=True, download_name='air_quality_data.csv')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== AIR QUALITY STANDARDS ====================

@api.route('/standards', methods=['GET'])
def get_standards():
    """Get air quality standards"""
    return jsonify({
        'success': True,
        'standards': {
            'co2': AirQualityStandards.CO2_STANDARDS,
            'co': AirQualityStandards.CO_STANDARDS
        }
    }), 200
