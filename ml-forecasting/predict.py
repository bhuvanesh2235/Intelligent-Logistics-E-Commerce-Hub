"""
predict.py -- Phase 5: Inference & Future Forecasting
Module 2 | Intelligent Logistics & E-Commerce Hub
"""
import os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

from utils import get_logger, save_fig, save_json, MODEL_DIR, detect_trend
from utils import ACCENT, BLUE, GREEN, RED, ORANGE, DARK_BG
import joblib
from dotenv import load_dotenv

load_dotenv()
logger = get_logger("predict")

LOOKBACK = int(os.getenv("LOOKBACK_DAYS", 30))
HORIZON  = int(os.getenv("FORECAST_HORIZON", 7))


# ── Load model + scaler ───────────────────────────────────────────────────────
def load_artifacts(task: str):
    model_path  = os.path.join(MODEL_DIR, f"lstm_{task}.keras")
    scaler_path = os.path.join(MODEL_DIR, f"scaler_{task}.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Train the model first: {model_path}")
    model  = tf.keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)
    logger.info(f"Loaded model+scaler for task='{task}'")
    return model, scaler


# ── Get last N values from dataset ────────────────────────────────────────────
def get_last_window(task: str, lookback: int = LOOKBACK) -> np.ndarray:
    csv = "data/daily_sales.csv" if task == "sales" else "data/shipment_demand.csv"
    col = "sales" if task == "sales" else "shipments"
    df  = pd.read_csv(csv)
    return df[col].values[-lookback:]


# ── Recursive multi-step forecast ─────────────────────────────────────────────
def forecast_future(task: str, horizon: int = HORIZON,
                    custom_window: np.ndarray = None) -> dict:
    """
    Recursively predict `horizon` future steps using the last `lookback` values.
    Returns predictions in original scale with trend and confidence bounds.
    """
    model, scaler = load_artifacts(task)

    window_raw = custom_window if custom_window is not None else get_last_window(task)
    window_scaled = scaler.transform(window_raw.reshape(-1, 1)).flatten()

    predictions_scaled = []
    current_window = list(window_scaled[-LOOKBACK:])

    for step in range(horizon):
        x_input = np.array(current_window[-LOOKBACK:]).reshape(1, LOOKBACK, 1)
        pred    = float(model.predict(x_input, verbose=0)[0][0])
        pred    = max(0.0, min(1.0, pred))   # clip to [0,1] (scaled range)
        predictions_scaled.append(pred)
        current_window.append(pred)

    # Inverse transform
    preds_orig = scaler.inverse_transform(
        np.array(predictions_scaled).reshape(-1, 1)
    ).flatten()
    preds_orig = np.maximum(preds_orig, 0)   # no negative volumes

    trend = detect_trend(preds_orig.tolist())

    # Confidence bands (±10% heuristic)
    lower = (preds_orig * 0.90).tolist()
    upper = (preds_orig * 1.10).tolist()

    result = {
        "task":          task,
        "forecast_days": horizon,
        "predicted":     [round(float(v), 2) for v in preds_orig],
        "lower_bound":   [round(float(v), 2) for v in lower],
        "upper_bound":   [round(float(v), 2) for v in upper],
        "trend":         trend,
        "avg_forecast":  round(float(preds_orig.mean()), 2),
        "peak_day":      int(np.argmax(preds_orig)) + 1,
        "peak_value":    round(float(preds_orig.max()), 2),
    }

    logger.info(f"Forecast [{task}] horizon={horizon} | trend={trend} | avg={result['avg_forecast']}")
    return result


# ── Forecast Plot ─────────────────────────────────────────────────────────────
def plot_forecast(task: str, horizon: int = HORIZON, history_days: int = 60):
    csv = "data/daily_sales.csv" if task == "sales" else "data/shipment_demand.csv"
    col = "sales" if task == "sales" else "shipments"
    df  = pd.read_csv(csv)
    historical = df[col].values[-history_days:]

    result = forecast_future(task, horizon)
    preds  = result["predicted"]
    lower  = result["lower_bound"]
    upper  = result["upper_bound"]

    hist_x = range(history_days)
    fore_x = range(history_days, history_days + horizon)

    fig, ax = plt.subplots(figsize=(14, 6), facecolor=DARK_BG)
    ax.plot(hist_x, historical, color=BLUE, lw=2, label="Historical", alpha=0.9)
    ax.plot(fore_x, preds, color=ACCENT, lw=2.5, marker="o", markersize=5,
            label=f"Forecast ({horizon}d)", linestyle="--")
    ax.fill_between(fore_x, lower, upper, alpha=0.15, color=ACCENT,
                    label="Confidence Band (±10%)")
    ax.axvline(history_days - 1, color="white", lw=1.5, linestyle=":", alpha=0.5)
    ax.text(history_days, ax.get_ylim()[1]*0.95, " Forecast\n Start",
            color="white", fontsize=9, alpha=0.7)
    ax.set_title(f"{task.title()} Forecast — Next {horizon} Days | Trend: {result['trend'].upper()}",
                 fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Days", color="white")
    ax.set_ylabel(col.title(), color="white")
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.2)
    save_fig(f"forecast_{task}_{horizon}d")
    logger.info(f"Forecast chart saved for task={task}")
    return result


# ── Batch forecast for both tasks ─────────────────────────────────────────────
def run_all_forecasts():
    all_results = {}
    for task in ["sales", "shipments"]:
        for horizon in [7, 30]:
            key    = f"{task}_{horizon}d"
            result = plot_forecast(task, horizon)
            all_results[key] = result
            save_json(result, f"forecast_{key}.json")
            print(f"\n[{key}] Forecast: {result['predicted'][:5]} ... trend={result['trend']}")
    return all_results


if __name__ == "__main__":
    run_all_forecasts()
