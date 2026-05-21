"""
sequence_builder.py -- Phase 2: LSTM Sequence Generation
Module 2 | Intelligent Logistics & E-Commerce Hub
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib, os
from utils import get_logger, MODEL_DIR
from dotenv import load_dotenv

load_dotenv()
logger = get_logger("sequence_builder")

LOOKBACK_DAYS  = int(os.getenv("LOOKBACK_DAYS",  30))
LOOKBACK_WEEKS = int(os.getenv("LOOKBACK_WEEKS", 12))


def create_sequences(data: np.ndarray, lookback: int) -> tuple:
    """
    Slide a window of size `lookback` over `data`.
    Returns X shape (samples, lookback, 1) and y shape (samples,).
    """
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i - lookback:i])
        y.append(data[i])
    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)   # (samples, timesteps, features)
    logger.info(f"Sequences created: X={X.shape}, y={y.shape}")
    return X, y


def create_multivariate_sequences(df: pd.DataFrame, target_col: str,
                                   feature_cols: list, lookback: int) -> tuple:
    """
    Multi-feature LSTM sequences.
    Returns X shape (samples, lookback, n_features) and y shape (samples,).
    """
    # Scale all features together
    scaler = MinMaxScaler()
    features = df[feature_cols].values
    target   = df[[target_col]].values

    feat_scaled   = scaler.fit_transform(features)
    target_scaler = MinMaxScaler()
    target_scaled = target_scaler.fit_transform(target).flatten()

    X, y = [], []
    for i in range(lookback, len(feat_scaled)):
        X.append(feat_scaled[i - lookback:i])
        y.append(target_scaled[i])
    X, y = np.array(X), np.array(y)
    logger.info(f"Multivariate sequences: X={X.shape}, y={y.shape}")
    return X, y, scaler, target_scaler


def train_val_test_split(X: np.ndarray, y: np.ndarray,
                          val_ratio: float = 0.15,
                          test_ratio: float = 0.10) -> tuple:
    n = len(X)
    test_sz = int(n * test_ratio)
    val_sz  = int(n * val_ratio)
    train_sz = n - val_sz - test_sz

    X_train = X[:train_sz]
    X_val   = X[train_sz:train_sz + val_sz]
    X_test  = X[train_sz + val_sz:]
    y_train = y[:train_sz]
    y_val   = y[train_sz:train_sz + val_sz]
    y_test  = y[train_sz + val_sz:]

    logger.info(f"Split -> Train:{len(X_train)} | Val:{len(X_val)} | Test:{len(X_test)}")
    return X_train, X_val, X_test, y_train, y_val, y_test


def build_sequences_for_task(task: str = "sales") -> dict:
    """
    Full sequence-building pipeline for a given task.
    task: 'sales' or 'shipments'
    """
    if task == "sales":
        csv_path  = "data/daily_sales.csv"
        target    = "sales"
        lookback  = LOOKBACK_DAYS
    else:
        csv_path  = "data/shipment_demand.csv"
        target    = "shipments"
        lookback  = LOOKBACK_DAYS

    df = pd.read_csv(csv_path)
    logger.info(f"Building sequences for '{task}' | rows={len(df)} | lookback={lookback}")

    # Univariate (primary LSTM input)
    scaler_path = os.path.join(MODEL_DIR, f"scaler_{task}.pkl")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        scaled = scaler.transform(df[[target]].values).flatten()
    else:
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(df[[target]].values).flatten()
        joblib.dump(scaler, scaler_path)

    X, y = create_sequences(scaled, lookback)
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split(X, y)

    # Save raw values for inverse transform
    np.save(os.path.join("data", f"{task}_scaled.npy"), scaled)

    return {
        "X_train": X_train, "X_val": X_val, "X_test": X_test,
        "y_train": y_train, "y_val": y_val, "y_test": y_test,
        "scaler":  scaler,  "lookback": lookback,
        "raw":     df[target].values,
        "dates":   df["date"].values,
    }


if __name__ == "__main__":
    for task in ["sales", "shipments"]:
        result = build_sequences_for_task(task)
        print(f"[{task}] X_train={result['X_train'].shape}, X_test={result['X_test'].shape}")
