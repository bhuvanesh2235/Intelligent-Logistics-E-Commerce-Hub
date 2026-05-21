# ⚡ Module 2 — LSTM Sales & Shipment Forecasting

> **Intelligent Logistics & E-Commerce Hub** | AI-powered time-series demand forecasting using deep LSTM networks.

![Module](https://img.shields.io/badge/Module-2%20--%20LSTM%20Forecasting-6c63ff?style=flat-square)
![Stack](https://img.shields.io/badge/Stack-TensorFlow%20%7C%20Flask%20%7C%20pandas-00d4aa?style=flat-square)

---

## Overview

This module builds a production-ready LSTM forecasting system that:
- Aggregates raw e-commerce orders into daily/weekly time-series
- Engineers temporal features (lag, rolling mean, seasonality)
- Trains a 2-layer LSTM model for sales and shipment demand
- Exposes forecasts via a Flask REST API
- Generates interactive dark-theme visualisation charts

---

## Project Structure

```
ml-forecasting/
├── data/                      # Generated time-series CSVs
├── models/                    # Trained .keras + .pkl artifacts
├── outputs/
│   ├── charts/                # PNG visualisation charts
│   ├── forecasting.log
│   └── *.json                 # Metadata & evaluation results
├── notebooks/                 # Jupyter notebooks (optional)
│
├── preprocessing.py           # Phase 1 — time-series preparation
├── sequence_builder.py        # Phase 2 — LSTM sequence creation
├── train_lstm.py              # Phase 3 — model + training
├── evaluate.py                # Phase 4 — metrics & charts
├── predict.py                 # Phase 5 — inference & forecast
├── app.py                     # Phase 6 — Flask API
├── utils.py                   # Shared utilities
├── requirements.txt
├── .env
└── README.md
```

---

## Setup

### 1. Install dependencies
```bash
cd ml-forecasting
pip install -r requirements.txt
```

### 2. Run full pipeline
```bash
# Step 1 — Generate time-series data
python preprocessing.py

# Step 2 — Train LSTM models (sales + shipments)
python train_lstm.py

# Step 3 — Evaluate models
python evaluate.py

# Step 4 — Generate forecasts + charts
python predict.py

# Step 5 — Start Flask API
python app.py
```

---

## Flask API

Base URL: `http://localhost:5001`

### GET `/health`
```json
{ "status": "ok", "module": "Module 2 — LSTM Forecasting" }
```

### POST `/api/v2/forecast/sales`
```json
// Request
{ "horizon": 7 }

// Response
{
  "status": "success",
  "task": "sales",
  "forecast_days": 7,
  "trend": "upward",
  "avg_forecast": 138.5,
  "peak_day": 4,
  "peak_value": 162.0,
  "predictions": [130, 135, 142, 162, 155, 148, 139],
  "lower_bound":  [117, 121, 127, 145, 139, 133, 125],
  "upper_bound":  [143, 148, 156, 178, 170, 162, 153],
  "dates": ["2025-05-16", "2025-05-17", ...],
  "chart_data": [{ "date": "2025-05-16", "value": 130, "lower": 117, "upper": 143 }, ...]
}
```

### POST `/api/v2/forecast/shipment-demand`
Same structure as sales, task = `"shipments"`.

### GET `/api/v2/forecast/sales/quick?horizon=7`
Quick GET with no body — returns 7-day forecast.

---

## LSTM Architecture

```
Input(lookback=30, features=1)
    └── LSTM(128, return_sequences=True)
    └── Dropout(0.2)
    └── LSTM(64)
    └── Dropout(0.2)
    └── Dense(32, relu)
    └── Dense(1, linear)  -- forecast output
```

**Training Config:**
| Parameter       | Value     |
|-----------------|-----------|
| Optimizer       | Adam      |
| Loss            | MSE       |
| Early Stopping  | patience=12 |
| LR Scheduler    | ReduceLROnPlateau |
| Max Epochs      | 60        |
| Batch Size      | 32        |
| Lookback Window | 30 days   |

---

## Evaluation Metrics

| Metric | Description                         |
|--------|-------------------------------------|
| MAE    | Mean Absolute Error                 |
| RMSE   | Root Mean Squared Error             |
| MAPE   | Mean Absolute Percentage Error (%)  |
| R²     | Coefficient of Determination        |

---

## Generated Charts

| Chart                          | Description                        |
|--------------------------------|------------------------------------|
| `loss_curve_sales.png`         | Training vs validation loss        |
| `actual_vs_predicted_sales.png`| Overlay of ground truth vs LSTM    |
| `residuals_sales.png`          | Residual over time + distribution  |
| `moving_average_sales.png`     | MA-7, MA-14, MA-30 trend lines     |
| `seasonal_analysis_sales.png`  | Monthly + day-of-week patterns     |
| `forecast_sales_7d.png`        | 7-day ahead forecast with CI band  |
| `forecast_sales_30d.png`       | 30-day ahead forecast              |
| *(same set for shipments)*     |                                    |

---

## Forecasting Methodology

1. **Data Aggregation** — raw orders → daily order counts by order date
2. **Feature Engineering** — rolling means (MA-7/14/30), lag features (1/3/7/14), pct-change, seasonality flags
3. **Sequence Creation** — sliding window of 30 days → next day label
4. **Scaling** — MinMaxScaler (0,1) applied per-task; scaler saved for inference
5. **LSTM Training** — chronological 75/15/10 train/val/test split
6. **Recursive Forecasting** — autoregressive: each prediction feeds into the next input window
7. **Confidence Bands** — ±10% heuristic bounds around point estimates

---

## Future Improvements (Module 3)
- CNN parcel damage detection
- Attention mechanisms on LSTM
- Multivariate LSTM (weather, promotions)
- Probabilistic forecasting (Monte Carlo Dropout)
