"""
preprocessing.py -- Full Data Preprocessing Pipeline
Adapted for: E-Commerce Order Fulfillment Dataset (50K Records)
Columns: Order_ID, Customer_Region, Product_Category, Order_Date,
         Ship_Date, Delivery_Date, Shipping_Mode, Shipping_Cost,
         Delivery_Status, Delivery_Days
"""

import os, logging, warnings
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from scipy import stats
import joblib

warnings.filterwarnings("ignore")

# ── Logging ──────────────────────────────────────────────────────────────────
os.makedirs("outputs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("outputs/preprocessing.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_DATA_PATH      = "data/raw/ecommerce_shipping.csv"
PROCESSED_DATA_PATH = "data/processed/cleaned_dataset.csv"
SCALER_PATH        = "outputs/scaler.pkl"
ENCODERS_PATH      = "outputs/encoders.pkl"

os.makedirs("data/processed", exist_ok=True)


# ── 1. Load ───────────────────────────────────────────────────────────────────
def load_data(path: str) -> pd.DataFrame:
    logger.info(f"Loading: {path}")
    df = pd.read_csv(path)
    logger.info(f"Raw shape: {df.shape} | Columns: {list(df.columns)}")
    return df


# ── 2. Rename to standard names ───────────────────────────────────────────────
COLUMN_MAP = {
    "Order_ID":         "order_id",
    "Customer_Region":  "customer_region",
    "Product_Category": "product_category",
    "Order_Date":       "order_date",
    "Ship_Date":        "ship_date",
    "Delivery_Date":    "delivery_date",
    "Shipping_Mode":    "shipping_mode",
    "Shipping_Cost":    "shipping_cost",
    "Delivery_Status":  "delivery_status",
    "Delivery_Days":    "delivery_days",
}

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})
    logger.info(f"Columns after rename: {list(df.columns)}")
    return df


# ── 3. Missing values ─────────────────────────────────────────────────────────
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isnull().sum()
    logger.info(f"Missing before:\n{missing[missing > 0]}")

    num_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=["object"]).columns

    if len(num_cols):
        df[num_cols] = SimpleImputer(strategy="median").fit_transform(df[num_cols])
    if len(cat_cols):
        df[cat_cols] = SimpleImputer(strategy="most_frequent").fit_transform(df[cat_cols])

    logger.info(f"Missing after: {df.isnull().sum().sum()}")
    return df


# ── 4. Duplicates ─────────────────────────────────────────────────────────────
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    logger.info(f"Duplicates removed: {before - len(df)} | Shape: {df.shape}")
    return df


# ── 5. Parse dates & compute lag days ─────────────────────────────────────────
def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["order_date", "ship_date", "delivery_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if {"order_date", "ship_date"}.issubset(df.columns):
        df["order_to_ship_days"] = (df["ship_date"] - df["order_date"]).dt.days.clip(lower=0)

    if {"ship_date", "delivery_date"}.issubset(df.columns):
        df["ship_to_delivery_days"] = (df["delivery_date"] - df["ship_date"]).dt.days.clip(lower=0)

    if "order_date" in df.columns:
        df["order_month"]    = df["order_date"].dt.month
        df["order_dayofweek"] = df["order_date"].dt.dayofweek

    # Drop raw date columns (not useful for ML after feature extraction)
    df = df.drop(columns=["order_date", "ship_date", "delivery_date"], errors="ignore")
    logger.info("Date parsing complete.")
    return df


# ── 6. Encode target & categoricals ──────────────────────────────────────────
def encode_categoricals(df: pd.DataFrame) -> tuple:
    encoders = {}

    # Binary target: Delivered=1, else=0
    if "delivery_status" in df.columns:
        df["delivered_on_time"] = (df["delivery_status"].str.strip().str.lower() == "delivered").astype(int)
        df = df.drop(columns=["delivery_status"])
        logger.info("Target 'delivered_on_time' created (Delivered=1, Delayed=0)")

    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    cat_cols = [c for c in cat_cols if c != "order_id"]

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        logger.info(f"  Encoded '{col}': {list(le.classes_)}")

    return df, encoders


# ── 7. Outlier removal ────────────────────────────────────────────────────────
def handle_outliers(df: pd.DataFrame, z_thresh: float = 3.5) -> pd.DataFrame:
    exclude = ["order_id", "delivered_on_time", "order_month", "order_dayofweek"]
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    before = len(df)
    z = np.abs(stats.zscore(df[num_cols].fillna(0)))
    df = df[(z < z_thresh).all(axis=1)].reset_index(drop=True)
    logger.info(f"Outliers removed: {before - len(df)} | Shape: {df.shape}")
    return df


# ── 8. Feature Engineering ────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # delivery_delay_days: actual - expected (approx expected = 7 days)
    if "delivery_days" in df.columns:
        df["delivery_delay_days"] = (df["delivery_days"] - 7).clip(lower=0).round(2)

    # shipping_efficiency_score: lower cost + on-time = efficient
    if {"shipping_cost", "delivered_on_time"}.issubset(df.columns):
        cost_norm = (df["shipping_cost"] - df["shipping_cost"].min()) / \
                    (df["shipping_cost"].max() - df["shipping_cost"].min() + 1e-9)
        df["shipping_efficiency_score"] = (
            (1 - cost_norm) * 0.6 + df["delivered_on_time"] * 0.4
        ).round(4)

    # warehouse_load_score: frequency of region as proxy
    if "customer_region" in df.columns:
        freq = df["customer_region"].value_counts(normalize=True)
        df["warehouse_load_score"] = df["customer_region"].map(freq).round(4)

    # customer_order_frequency: uniform proxy (no prior_purchases in this dataset)
    df["customer_order_frequency"] = 0.5  # placeholder

    # avg_delivery_time: same as delivery_days
    if "delivery_days" in df.columns:
        df["avg_delivery_time"] = df["delivery_days"].round(2)

    # priority_shipping_flag: high cost + express mode
    if {"shipping_cost", "shipping_mode"}.issubset(df.columns):
        cost_thresh = df["shipping_cost"].quantile(0.75)
        df["priority_shipping_flag"] = (
            (df["shipping_cost"] >= cost_thresh)
        ).astype(int)

    # cost_per_day: shipping cost divided by delivery days
    if {"shipping_cost", "delivery_days"}.issubset(df.columns):
        df["cost_per_day"] = (df["shipping_cost"] / (df["delivery_days"] + 1)).round(2)

    # is_weekend_order
    if "order_dayofweek" in df.columns:
        df["is_weekend_order"] = (df["order_dayofweek"] >= 5).astype(int)

    # is_peak_month: Nov, Dec = peak
    if "order_month" in df.columns:
        df["is_peak_month"] = df["order_month"].isin([11, 12]).astype(int)

    logger.info(f"Feature engineering done. Shape: {df.shape}")
    return df


# ── 9. Scale features ─────────────────────────────────────────────────────────
def scale_features(df: pd.DataFrame) -> tuple:
    exclude = [
        "order_id", "delivered_on_time", "priority_shipping_flag",
        "is_weekend_order", "is_peak_month", "order_month",
        "order_dayofweek", "shipping_mode", "customer_region", "product_category",
    ]
    scale_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[scale_cols] = scaler.fit_transform(df[scale_cols])
    logger.info(f"Scaled {len(scale_cols)} features.")
    return df_scaled, scaler


# ── 10. Save ──────────────────────────────────────────────────────────────────
def save_artifacts(df: pd.DataFrame, scaler, encoders: dict):
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    joblib.dump(scaler,   SCALER_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    logger.info(f"Saved cleaned CSV  --> {PROCESSED_DATA_PATH}")
    logger.info(f"Saved scaler       --> {SCALER_PATH}")
    logger.info(f"Saved encoders     --> {ENCODERS_PATH}")


# ── 11. Summary ───────────────────────────────────────────────────────────────
def print_summary(orig: pd.DataFrame, proc: pd.DataFrame):
    lines = [
        "=" * 55,
        "  PREPROCESSING SUMMARY",
        "=" * 55,
        f"  Original rows      : {len(orig):,}",
        f"  Processed rows     : {len(proc):,}",
        f"  Rows removed       : {len(orig) - len(proc):,}",
        f"  Original columns   : {len(orig.columns)}",
        f"  Processed columns  : {len(proc.columns)}",
        f"  New features added : {len(proc.columns) - len(orig.columns)}",
        "=" * 55,
        "  FINAL COLUMNS:",
    ] + [f"    - {c}" for c in proc.columns] + ["=" * 55]

    print("\n".join(lines))
    with open("outputs/preprocessing_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── Main Pipeline ─────────────────────────────────────────────────────────────
def run_pipeline():
    logger.info("=" * 55)
    logger.info("STARTING PREPROCESSING PIPELINE")
    logger.info("=" * 55)

    df_raw = load_data(RAW_DATA_PATH)
    df = rename_columns(df_raw.copy())
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = parse_dates(df)
    df, encoders = encode_categoricals(df)
    df = handle_outliers(df)
    df = engineer_features(df)
    df_scaled, scaler = scale_features(df)
    save_artifacts(df_scaled, scaler, encoders)
    print_summary(df_raw, df_scaled)

    logger.info("Pipeline complete.")
    return df_scaled


if __name__ == "__main__":
    df = run_pipeline()
    print(f"\nSample output:\n{df.head(3).to_string()}")
