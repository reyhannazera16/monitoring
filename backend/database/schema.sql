-- Air Quality Monitoring Database Schema

-- Sensor readings table
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location TEXT NOT NULL DEFAULT 'Perkotaan', -- New: 'Perkotaan' or 'Pedesaan'
    co2_ppm REAL NOT NULL,
    co_ppm REAL NOT NULL,
    mq7_detected BOOLEAN NOT NULL DEFAULT 0,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_date DATETIME NOT NULL,
    location TEXT NOT NULL DEFAULT 'Perkotaan',
    parameter_type TEXT NOT NULL, -- 'co2' or 'co'
    predicted_value REAL NOT NULL,
    confidence_lower REAL NOT NULL,
    confidence_upper REAL NOT NULL,
    model_params TEXT, -- JSON string of ARIMA (p,d,q) parameters
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Air quality events table
CREATE TABLE IF NOT EXISTS air_quality_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location TEXT NOT NULL DEFAULT 'Perkotaan',
    event_type TEXT NOT NULL, -- 'threshold_crossed', 'warning', 'danger'
    parameter TEXT NOT NULL, -- 'co2' or 'co'
    severity TEXT NOT NULL, -- 'baik', 'sedang', 'tidak_sehat', etc.
    value REAL NOT NULL,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Model metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL DEFAULT 'Perkotaan',
    parameter_type TEXT NOT NULL,
    model_params TEXT NOT NULL, -- JSON string
    aic REAL,
    bic REAL,
    training_samples INTEGER,
    trained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp, location);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date, location);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions(parameter_type, location);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON air_quality_events(timestamp, location);
CREATE INDEX IF NOT EXISTS idx_model_active ON model_metadata(is_active, parameter_type, location);
