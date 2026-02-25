# Quick Start Script for Air Quality Prediction System
# This script automates the setup process

Write-Host "================================" -ForegroundColor Cyan
Write-Host " AIR QUALITY PREDICTION SYSTEM" -ForegroundColor Cyan
Write-Host " Quick Start Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8 or higher" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host ""
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\activate.ps1"
pip install -r backend/requirements.txt --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Generate sample data
Write-Host ""
Write-Host "[4/5] Generating sample data..." -ForegroundColor Yellow
if (Test-Path "data/air_quality.db") {
    Write-Host "✓ Database already exists" -ForegroundColor Green
} else {
    python backend/utils/sample_data_generator.py
    Write-Host "✓ Sample data generated" -ForegroundColor Green
}

# Train models
Write-Host ""
Write-Host "[5/5] Training ARIMA models..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan

$trainScript = @"
from backend.database.db_manager import DatabaseManager
from backend.models.predictor import PredictionEngine
from backend.config import Config

db_manager = DatabaseManager(Config.DATABASE_PATH)
engine = PredictionEngine(db_manager)
print('Training models...')
engine.train_models(training_days=180)
print('Generating predictions...')
engine.generate_predictions(periods=365)
print('✓ Models trained successfully!')
"@

$trainScript | python

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host " SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Cyan
Write-Host "  python backend/app.py" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser to:" -ForegroundColor Cyan
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
