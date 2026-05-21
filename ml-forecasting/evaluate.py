"""
evaluate.py -- Phase 4: Model Evaluation & Visualization
Module 2 | Intelligent Logistics & E-Commerce Hub
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf

from utils import get_logger, save_fig, save_json, MODEL_DIR, moving_average
from utils import ACCENT, BLUE, GREEN, RED, ORANGE, DARK_BG, PANEL
from sequence_builder import build_sequences_for_task

logger = get_logger("evaluate")


# ── Metrics ───────────────────────────────────────────────────────────────────
def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae  = mean_absolute_error(y_true, y_pred)
    mse  = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_true, y_pred)
    # MAPE — avoid division by zero
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if mask.any() else 0.0
    return {
        "MAE":  round(float(mae),  4),
        "RMSE": round(float(rmse), 4),
        "MAPE": round(float(mape), 4),
        "R2":   round(float(r2),   4),
    }


# ── Actual vs Predicted Plot ──────────────────────────────────────────────────
def plot_actual_vs_predicted(actual: np.ndarray, predicted: np.ndarray,
                              task: str, dates=None, subset: int = 200):
    n = min(len(actual), subset)
    x = range(n)
    fig, ax = plt.subplots(figsize=(14, 5), facecolor=DARK_BG)
    ax.plot(x, actual[:n],    color=BLUE,   lw=1.8, label="Actual",    alpha=0.9)
    ax.plot(x, predicted[:n], color=ACCENT, lw=1.8, label="Predicted", linestyle="--", alpha=0.9)
    ax.fill_between(x, actual[:n], predicted[:n], alpha=0.08, color=ACCENT)
    ax.set_title(f"Actual vs Predicted — {task.title()} Forecasting",
                 fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Time Steps", color="white")
    ax.set_ylabel("Value (original scale)", color="white")
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.25)
    save_fig(f"actual_vs_predicted_{task}")


# ── Residuals Plot ────────────────────────────────────────────────────────────
def plot_residuals(actual: np.ndarray, predicted: np.ndarray, task: str):
    residuals = actual - predicted
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor=DARK_BG)
    fig.suptitle(f"Residual Analysis — {task.title()}", fontsize=14,
                 color="white", fontweight="bold")
    # Residual over time
    axes[0].plot(residuals, color=RED, lw=1.2, alpha=0.8)
    axes[0].axhline(0, color="white", lw=1, linestyle="--")
    axes[0].set_title("Residuals Over Time", color="white")
    axes[0].set_ylabel("Error", color="white")
    # Distribution
    axes[1].hist(residuals, bins=40, color=ACCENT, edgecolor=DARK_BG, alpha=0.85)
    axes[1].axvline(0, color=RED, lw=2, linestyle="--")
    axes[1].set_title("Residual Distribution", color="white")
    axes[1].set_xlabel("Error", color="white")
    plt.tight_layout()
    save_fig(f"residuals_{task}")


# ── Moving Average Trend ──────────────────────────────────────────────────────
def plot_moving_average(actual: np.ndarray, task: str):
    ma7  = moving_average(actual, 7)
    ma14 = moving_average(actual, 14)
    ma30 = moving_average(actual, 30)
    fig, ax = plt.subplots(figsize=(14, 5), facecolor=DARK_BG)
    ax.plot(actual, color="white", lw=0.8, alpha=0.3, label="Raw")
    ax.plot(range(6,  len(actual)), ma7,  color=BLUE,   lw=2, label="MA-7")
    ax.plot(range(13, len(actual)), ma14, color=GREEN,  lw=2, label="MA-14")
    ax.plot(range(29, len(actual)), ma30, color=ACCENT, lw=2, label="MA-30")
    ax.set_title(f"Moving Average Trend — {task.title()}",
                 fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Days", color="white")
    ax.set_ylabel("Volume", color="white")
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.25)
    save_fig(f"moving_average_{task}")


# ── Seasonal Analysis ─────────────────────────────────────────────────────────
def plot_seasonal_analysis(task: str = "sales"):
    csv = "data/daily_sales.csv" if task == "sales" else "data/shipment_demand.csv"
    col = "sales" if task == "sales" else "shipments"
    df  = pd.read_csv(csv)
    df["date"]  = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["dow"]   = df["date"].dt.dayofweek
    DOW_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    MON_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 5), facecolor=DARK_BG)
    fig.suptitle(f"Seasonal Analysis — {task.title()}", fontsize=14,
                 color="white", fontweight="bold")

    # Monthly
    monthly = df.groupby("month")[col].mean()
    axes[0].bar(range(len(monthly)), monthly.values, color=BLUE, edgecolor=DARK_BG)
    axes[0].set_xticks(range(len(monthly)))
    axes[0].set_xticklabels([MON_LABELS[i-1] for i in monthly.index], rotation=30)
    axes[0].set_title("Avg by Month", color="white")
    axes[0].set_ylabel(f"Avg {col}", color="white")

    # Day of week
    dow = df.groupby("dow")[col].mean()
    colors = [ACCENT if i >= 5 else BLUE for i in dow.index]
    axes[1].bar(range(len(dow)), dow.values, color=colors, edgecolor=DARK_BG)
    axes[1].set_xticks(range(len(dow)))
    axes[1].set_xticklabels([DOW_LABELS[i] for i in dow.index])
    axes[1].set_title("Avg by Day of Week (purple=weekend)", color="white")
    axes[1].set_ylabel(f"Avg {col}", color="white")

    plt.tight_layout()
    save_fig(f"seasonal_analysis_{task}")


# ── Full Evaluation ───────────────────────────────────────────────────────────
def evaluate(task: str = "sales") -> dict:
    logger.info("=" * 55)
    logger.info(f"EVALUATING MODEL: {task.upper()}")
    logger.info("=" * 55)

    model_path = os.path.join(MODEL_DIR, f"lstm_{task}.keras")
    if not os.path.exists(model_path):
        logger.error(f"Model not found: {model_path} — run train_lstm.py first.")
        return {}

    model = tf.keras.models.load_model(model_path)
    seqs  = build_sequences_for_task(task)
    scaler = seqs["scaler"]

    # Predict on test set
    y_pred_scaled = model.predict(seqs["X_test"], verbose=0).flatten()
    y_test_scaled = seqs["y_test"]

    # Inverse transform
    y_pred = scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    y_true = scaler.inverse_transform(y_test_scaled.reshape(-1, 1)).flatten()

    metrics = compute_metrics(y_true, y_pred)
    logger.info(f"Metrics: {metrics}")

    # Plots
    plot_actual_vs_predicted(y_true, y_pred, task)
    plot_residuals(y_true, y_pred, task)
    plot_moving_average(seqs["raw"], task)
    plot_seasonal_analysis(task)

    # Performance summary
    summary = {
        "task":    task,
        "metrics": metrics,
        "test_samples": len(y_true),
        "model_path":   model_path,
    }
    save_json(summary, f"evaluation_{task}.json")

    print(f"\n{'='*40}")
    print(f"  EVALUATION SUMMARY — {task.upper()}")
    print(f"{'='*40}")
    for k, v in metrics.items():
        bar = "=" * int(min(v, 40) if k != "R2" else v * 40)
        print(f"  {k:<6}: {v:>10.4f}  {bar}")
    print(f"{'='*40}\n")

    return summary


if __name__ == "__main__":
    for task in ["sales", "shipments"]:
        evaluate(task)
