# Air Quality Prediction System - Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Arduino IDE (for uploading Arduino code)
- ESP8266 board with MQ135 and MQ7 sensors

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to project directory
cd "d:\Projec\RULS IT\Dimas\monitoring_udara_prediction"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Generate Sample Data

```bash
# Run sample data generator
python backend/utils/sample_data_generator.py
```

This will create:
- `data/sample_data.csv` - CSV file with historical data
- `data/air_quality.db` - SQLite database with sensor readings

### 3. Train ARIMA Models

```bash
# Start Python interpreter
python

# Run training script
>>> from backend.database.db_manager import DatabaseManager
>>> from backend.models.predictor import PredictionEngine
>>> from backend.config import Config
>>> 
>>> db_manager = DatabaseManager(Config.DATABASE_PATH)
>>> engine = PredictionEngine(db_manager)
>>> engine.train_models(training_days=180)
>>> engine.generate_predictions(periods=365)
>>> exit()
```

### 4. Start Flask Server

```bash
# Run Flask application
python backend/app.py
```

The server will start on `http://localhost:5000`

### 5. Access Dashboard

Open your web browser and navigate to:
```
http://localhost:5000
```

## Arduino Setup (Optional)

If you want to send real-time data from Arduino:

1. Open `arduino/monitoring_udara_wifi.ino` in Arduino IDE

2. Update WiFi credentials:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

3. Update server URL (use your computer's IP address):
```cpp
const char* serverUrl = "http://192.168.1.100:5000/api/log";
```

4. Install required libraries:
   - ESP8266WiFi
   - ESP8266HTTPClient
   - ArduinoJson
   - LiquidCrystal_I2C

5. Upload to ESP8266 board

## API Endpoints

### Data Logging
- `POST /api/log` - Log sensor data

### Data Retrieval
- `GET /api/data/historical` - Get historical data
- `GET /api/data/latest` - Get latest reading
- `GET /api/statistics` - Get summary statistics

### Predictions
- `GET /api/predictions/co2` - Get CO2 predictions
- `GET /api/predictions/co` - Get CO predictions
- `GET /api/analysis/survival` - Get survival time analysis

### Model Management
- `POST /api/model/train` - Train ARIMA models

### Export
- `GET /api/export/csv` - Export data as CSV

### Standards
- `GET /api/standards` - Get air quality standards

## Troubleshooting

### No data in dashboard
1. Make sure you've run the sample data generator
2. Check that the database file exists in `data/air_quality.db`
3. Verify Flask server is running

### No predictions available
1. Train the models using the training script above
2. Check console for error messages
3. Ensure you have at least 30 days of historical data

### Arduino not connecting
1. Verify WiFi credentials are correct
2. Check that server URL uses correct IP address
3. Ensure Flask server is accessible from Arduino's network
4. Check Serial Monitor for connection status

## Production Deployment

For production deployment:

1. Change `DEBUG = False` in `backend/config.py`
2. Set a secure `SECRET_KEY` environment variable
3. Use PostgreSQL instead of SQLite
4. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## Support

For issues or questions, please check the documentation in the `docs/` directory.
