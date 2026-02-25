# ARIMA Methodology Documentation

## Overview

This system uses ARIMA (AutoRegressive Integrated Moving Average) time series forecasting to predict future air quality levels based on historical sensor data.

## ARIMA Model Components

### 1. AutoRegressive (AR) - p parameter
The AR component uses past values to predict future values. The parameter `p` represents the number of lag observations included in the model.

**Formula:**
```
y_t = c + φ₁y_{t-1} + φ₂y_{t-2} + ... + φₚy_{t-p} + ε_t
```

Where:
- y_t = current value
- φ = coefficients
- p = number of lags
- ε_t = error term

### 2. Integrated (I) - d parameter
The I component represents the number of times the data needs to be differenced to make it stationary. Stationarity is required for ARIMA models.

**Formula:**
```
y'_t = y_t - y_{t-1}  (first difference, d=1)
y''_t = y'_t - y'_{t-1}  (second difference, d=2)
```

### 3. Moving Average (MA) - q parameter
The MA component uses past forecast errors to predict future values. The parameter `q` represents the number of lagged forecast errors.

**Formula:**
```
y_t = μ + ε_t + θ₁ε_{t-1} + θ₂ε_{t-2} + ... + θₑε_{t-q}
```

Where:
- μ = mean
- θ = coefficients
- q = number of lags
- ε = error terms

## Parameter Selection

### Automatic Selection (pmdarima)
The system uses `auto_arima` from the pmdarima library to automatically find optimal parameters:

```python
model = auto_arima(
    data,
    start_p=0, max_p=5,    # AR order range
    start_d=0, max_d=2,    # Differencing range
    start_q=0, max_q=5,    # MA order range
    seasonal=False,         # No seasonal component
    stepwise=True,          # Stepwise search
    suppress_warnings=True,
    error_action='ignore'
)
```

### Selection Criteria

**AIC (Akaike Information Criterion)**
```
AIC = -2 * log(L) + 2 * k
```
Where:
- L = likelihood of the model
- k = number of parameters

Lower AIC indicates better model fit.

**BIC (Bayesian Information Criterion)**
```
BIC = -2 * log(L) + k * log(n)
```
Where:
- n = number of observations

BIC penalizes model complexity more than AIC.

## Data Preprocessing

### 1. Resampling
Raw sensor data is resampled to daily averages to reduce noise:
```python
series = series.resample('D').mean()
```

### 2. Missing Value Handling
- Forward fill: `series.fillna(method='ffill')`
- Backward fill: `series.fillna(method='bfill')`

### 3. Stationarity Testing
The Augmented Dickey-Fuller (ADF) test is used to check stationarity:
- H0: Series is non-stationary
- H1: Series is stationary
- If p-value < 0.05, reject H0 (series is stationary)

## Prediction Process

### 1. Model Training
```python
model = ARIMA(data, order=(p, d, q))
fitted_model = model.fit()
```

### 2. Forecasting
```python
forecast = fitted_model.get_forecast(steps=365)
predictions = forecast.predicted_mean
```

### 3. Confidence Intervals
95% confidence intervals are calculated:
```python
conf_int = forecast.conf_int(alpha=0.05)
lower_bound = conf_int[:, 0]
upper_bound = conf_int[:, 1]
```

## Model Evaluation

### Metrics Used

**1. AIC (Akaike Information Criterion)**
- Measures model quality
- Lower is better
- Balances fit and complexity

**2. BIC (Bayesian Information Criterion)**
- Similar to AIC
- Stronger penalty for complexity
- Preferred for model selection

**3. Mean Absolute Error (MAE)**
```
MAE = (1/n) * Σ|y_actual - y_predicted|
```

**4. Root Mean Square Error (RMSE)**
```
RMSE = √[(1/n) * Σ(y_actual - y_predicted)²]
```

## Threshold Crossing Detection

The system analyzes predictions to determine when air quality will cross critical thresholds:

### Algorithm
1. For each prediction point:
   - Compare predicted value with threshold
   - If value >= threshold, record date
2. Return first crossing date
3. Calculate days until crossing

### Thresholds Used

**CO₂ (ppm)**
- Sedang: 400
- Tidak Sehat: 1000
- Sangat Tidak Sehat: 2000
- Berbahaya: 5000

**CO (ppm)**
- Sedang: 4
- Tidak Sehat: 9
- Sangat Tidak Sehat: 15
- Berbahaya: 30

## Survival Time Calculation

### Best Case Scenario
Uses lower confidence bound (95% CI):
```python
best_case_value = confidence_lower
```

### Worst Case Scenario
Uses upper confidence bound (95% CI):
```python
worst_case_value = confidence_upper
```

### Expected Case
Uses predicted mean:
```python
expected_value = predicted_mean
```

## Limitations

1. **Data Quality**: Predictions are only as good as the input data
2. **Stationarity Assumption**: ARIMA assumes stationary data
3. **Linear Relationships**: ARIMA captures linear patterns, may miss non-linear trends
4. **External Factors**: Cannot account for sudden changes (e.g., new industrial activity)
5. **Long-term Predictions**: Accuracy decreases for longer forecast horizons

## Recommendations

1. **Regular Retraining**: Retrain models monthly with new data
2. **Validation**: Compare predictions with actual values
3. **Ensemble Methods**: Consider combining ARIMA with other models
4. **Seasonal Adjustment**: Add seasonal component if patterns exist
5. **Outlier Detection**: Remove or adjust outliers before training

## References

1. Box, G. E. P., & Jenkins, G. M. (1976). Time Series Analysis: Forecasting and Control
2. Hyndman, R. J., & Athanasopoulos, G. (2018). Forecasting: Principles and Practice
3. WHO Air Quality Guidelines (2021)
4. PP No. 22 Tahun 2021 - Indonesia Air Quality Standards
5. US EPA Air Quality Standards

## Implementation Details

### Libraries Used
- **statsmodels**: ARIMA model implementation
- **pmdarima**: Automatic parameter selection
- **pandas**: Time series data manipulation
- **numpy**: Numerical computations
- **scikit-learn**: Data preprocessing

### Model Persistence
Models are saved using pickle:
```python
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
```

This allows for:
- Fast prediction without retraining
- Consistent results across sessions
- Easy model versioning
