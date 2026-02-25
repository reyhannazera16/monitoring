"""
Configuration file for Air Quality Prediction System
"""
import os
from datetime import timedelta

class Config:
    # Base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    
    # Database
    DATABASE_PATH = os.path.join(PROJECT_ROOT, 'data', 'air_quality.db')
    
    # ARIMA Model Parameters
    ARIMA_PARAMS = {
        'max_p': 5,
        'max_d': 2,
        'max_q': 5,
        'seasonal': False,
        'stepwise': True,
        'suppress_warnings': True,
        'error_action': 'ignore',
        'trace': False
    }
    
    # Prediction Settings
    PREDICTION_PERIODS = 365  # Days (12 months)
    CONFIDENCE_LEVEL = 0.95
    
    # Air Quality Standards (WHO, EPA, PP No. 22 Tahun 2021)
    CO2_STANDARDS = {
        'baik': {'min': 0, 'max': 400, 'label': 'Baik', 'color': '#10b981'},
        'sedang': {'min': 400, 'max': 1000, 'label': 'Sedang', 'color': '#fbbf24'},
        'tidak_sehat': {'min': 1000, 'max': 2000, 'label': 'Tidak Sehat', 'color': '#f97316'},
        'sangat_tidak_sehat': {'min': 2000, 'max': 5000, 'label': 'Sangat Tidak Sehat', 'color': '#ef4444'},
        'berbahaya': {'min': 5000, 'max': 10000, 'label': 'Berbahaya', 'color': '#a855f7'}
    }
    
    CO_STANDARDS = {
        'baik': {'min': 0, 'max': 4, 'label': 'Baik', 'color': '#10b981'},
        'sedang': {'min': 4, 'max': 9, 'label': 'Sedang', 'color': '#fbbf24'},
        'tidak_sehat': {'min': 9, 'max': 15, 'label': 'Tidak Sehat', 'color': '#f97316'},
        'sangat_tidak_sehat': {'min': 15, 'max': 30, 'label': 'Sangat Tidak Sehat', 'color': '#ef4444'},
        'berbahaya': {'min': 30, 'max': 100, 'label': 'Berbahaya', 'color': '#a855f7'}
    }
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # CORS Settings
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
    
    # Data Collection
    DATA_COLLECTION_INTERVAL = 2  # seconds
    
    # Export Settings
    EXPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'exports')
    MAX_EXPORT_ROWS = 100000
