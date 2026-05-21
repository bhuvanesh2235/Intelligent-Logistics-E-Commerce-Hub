"""
preprocessing.py -- Phase 1: Time-Series Data Preparation
Module 2 | Intelligent Logistics & E-Commerce Hub
"""
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
from utils import get_logger, save_json, MODEL_DIR, OUTPUT_DIR
from dotenv import load_dotenv

load_dotenv()
logger = get_logger("preprocessing")

RAW_PATH = os.getenv("RAW_DATA_SOURCE", "../ml-preprocessing/data/raw/ecommerce_shipping.csv")
OUT_DIR  = "data"
os.makedirs(OUT_DIR, exist_ok=True)


# ── 1. Load Raw Data ──────────────────────────────────────────────────────────
def load_raw() -> pd.DataFrame:
    logger.info(f"Loading raw data: {RAW_PATH}")
    df = pd.read_csv(RAW_PATH, parse_dates=["Order_Date", "Ship_Date", "Delivery_Date"],
                     dayfirst=False)
    logger.info(f"Raw shape: {df.shape}")
    return df


# ── 2. Build Daily Sales Timeseries ──────────────────────────────────────────
def build_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate order count per day as 'sales'."""
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    daily = (
        df.groupby("order_date")
        .agg(
            sales        = ("Order_ID", "count"),
            total_cost   = ("Shipping_Cost", "sum"),
            avg_cost     = ("Shipping_Cost", "mean"),
            delivered    = ("Delivery_Status", lambda x: (x == "Delivered").sum()),
        )
        .reset_index()
        .rename(columns={"order_date": "date"})
        .sort_values("date")
    )
    # Fill missing dates
    full_range = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_range).fillna(0).reset_index()
    daily.rename(columns={"index": "date"}, inplace=True)
    logger.info(f"Daily sales range: {daily['date'].min()} --> {daily['date'].max()} | {len(daily)} days")
    return daily


# ── 3. Build Weekly Sales Timeseries ─────────────────────────────────────────
def build_weekly_sales(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["week"] = df["order_date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = (
        df.groupby("week")
        .agg(
            sales       = ("Order_ID", "count"),
            total_cost  = ("Shipping_Cost", "sum"),
            avg_cost    = ("Shipping_Cost", "mean"),
            delivered   = ("Delivery_Status", lambda x: (x == "Delivered").sum()),
        )
        .reset_index()
        .rename(columns={"week": "date"})
        .sort_values("date")
    )
    logger.info(f"Weekly sales range: {len(weekly)} weeks")
    return weekly


# ── 4. Build Shipment Demand Timeseries ──────────────────────────────────────
def build_shipment_demand(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ship_date"] = pd.to_datetime(df["Ship_Date"], errors="coerce")
    daily = (
        df.groupby("ship_date")
        .agg(
            shipments   = ("Order_ID", "count"),
            avg_cost    = ("Shipping_Cost", "mean"),
            avg_days    = ("Delivery_Days", "mean"),
        )
        .reset_index()
        .rename(columns={"ship_date": "date"})
        .sort_values("date")
    )
    full_range = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_range).fillna(0).reset_index()
    daily.rename(columns={"index": "date"}, inplace=True)
    logger.info(f"Shipment demand range: {len(daily)} days")
    return daily


# ── 5. Feature Engineering for Timeseries ────────────────────────────────────
def add_time_features(df: pd.DataFrame, target_col: str = "sales") -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["dayofweek"]  = df["date"].dt.dayofweek
    df["month"]      = df["date"].dt.month
    df["quarter"]    = df["date"].dt.quarter
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
    df["is_peak"]    = df["month"].isin([11, 12]).astype(int)

    # Rolling features
    df[f"{target_col}_ma7"]  = df[target_col].rolling(7,  min_periods=1).mean()
    df[f"{target_col}_ma14"] = df[target_col].rolling(14, min_periods=1).mean()
    df[f"{target_col}_ma30"] = df[target_col].rolling(30, min_periods=1).mean()
    df[f"{target_col}_std7"] = df[target_col].rolling(7,  min_periods=1).std().fillna(0)

    # Lag features
    for lag in [1, 3, 7, 14]:
        df[f"{target_col}_lag{lag}"] = df[target_col].shift(lag).fillna(0)

    # Trend (pct change)
    df[f"{target_col}_pct1"] = df[target_col].pct_change(1).fillna(0).clip(-5, 5)
    df[f"{target_col}_pct7"] = df[target_col].pct_change(7).fillna(0).clip(-5, 5)

    logger.info(f"Time features added. Columns: {list(df.columns)}")
    return df


# ── 6. Scale & Save ───────────────────────────────────────────────────────────
def scale_and_save(series: np.ndarray, name: str) -> tuple:
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(series.reshape(-1, 1))
    path = os.path.join(MODEL_DIR, f"scaler_{name}.pkl")
    joblib.dump(scaler, path)
    logger.info(f"Scaler saved: {path}")
    return scaled.flatten(), scaler


# ── 7. Main Pipeline ──────────────────────────────────────────────────────────
def run_preprocessing():
    logger.info("=" * 55)
    logger.info("TIME-SERIES PREPROCESSING STARTED")
    logger.info("=" * 55)

    df_raw = load_raw()

    # Daily sales
    daily_sales = build_daily_sales(df_raw)
    daily_sales = add_time_features(daily_sales, "sales")
    daily_sales.to_csv("data/daily_sales.csv", index=False)
    logger.info(f"Saved data/daily_sales.csv ({len(daily_sales)} rows)")

    # Weekly sales
    weekly_sales = build_weekly_sales(df_raw)
    weekly_sales = add_time_features(weekly_sales, "sales")
    weekly_sales.to_csv("data/weekly_sales.csv", index=False)
    logger.info(f"Saved data/weekly_sales.csv ({len(weekly_sales)} rows)")

    # Shipment demand
    shipment_demand = build_shipment_demand(df_raw)
    shipment_demand = add_time_features(shipment_demand, "shipments")
    shipment_demand.to_csv("data/shipment_demand.csv", index=False)
    logger.info(f"Saved data/shipment_demand.csv ({len(shipment_demand)} rows)")

    # Scale targets
    sales_scaled, sales_scaler     = scale_and_save(daily_sales["sales"].values, "sales")
    shipment_scaled, ship_scaler   = scale_and_save(shipment_demand["shipments"].values, "shipments")

    # Save metadata
    meta = {
        "daily_sales_rows":    len(daily_sales),
        "weekly_sales_rows":   len(weekly_sales),
        "shipment_demand_rows":len(shipment_demand),
        "date_range": {
            "start": str(daily_sales["date"].min()),
            "end":   str(daily_sales["date"].max()),
        },
        "avg_daily_sales":    float(daily_sales["sales"].mean().round(2)),
        "avg_daily_shipments":float(shipment_demand["shipments"].mean().round(2)),
        "max_daily_sales":    int(daily_sales["sales"].max()),
    }
    save_json(meta, "preprocessing_meta.json")
    logger.info("Preprocessing complete.")
    return daily_sales, weekly_sales, shipment_demand


if __name__ == "__main__":
    run_preprocessing()
