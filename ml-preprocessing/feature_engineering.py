"""
feature_engineering.py — Domain Feature Engineering
Intelligent Logistics & E-Commerce Hub — Module 1
"""
import os, logging, warnings
import pandas as pd
import numpy as np
import joblib

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

os.makedirs("outputs", exist_ok=True)


def add_delivery_delay_days(df: pd.DataFrame) -> pd.DataFrame:
    """Proxy: more care calls + low rating → higher delay."""
    if {"customer_care_calls", "customer_rating"}.issubset(df.columns):
        df["delivery_delay_days"] = (
            df["customer_care_calls"] * 0.5 - df["customer_rating"] * 0.2
        ).clip(lower=0).round(2)
        logger.info("Feature added: delivery_delay_days")
    return df


def add_shipping_efficiency_score(df: pd.DataFrame) -> pd.DataFrame:
    """Efficiency = lighter weight + on-time delivery."""
    if {"weight_grams", "delivered_on_time"}.issubset(df.columns):
        w_min, w_max = df["weight_grams"].min(), df["weight_grams"].max()
        w_norm = (df["weight_grams"] - w_min) / (w_max - w_min + 1e-9)
        df["shipping_efficiency_score"] = (
            (1 - w_norm) * 0.6 + df["delivered_on_time"] * 0.4
        ).round(4)
        logger.info("Feature added: shipping_efficiency_score")
    return df


def add_warehouse_load_score(df: pd.DataFrame) -> pd.DataFrame:
    """Frequency of orders per warehouse block (normalized)."""
    if "warehouse_block" in df.columns:
        freq = df["warehouse_block"].value_counts(normalize=True)
        df["warehouse_load_score"] = df["warehouse_block"].map(freq).round(4)
        logger.info("Feature added: warehouse_load_score")
    return df


def add_customer_order_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """Normalized prior purchase count as order frequency proxy."""
    if "prior_purchases" in df.columns:
        max_pp = df["prior_purchases"].max()
        df["customer_order_frequency"] = (
            df["prior_purchases"] / max_pp if max_pp > 0 else 0
        ).round(4)
        logger.info("Feature added: customer_order_frequency")
    return df


def add_avg_delivery_time(df: pd.DataFrame) -> pd.DataFrame:
    """Estimated delivery time in days based on weight and call volume."""
    if {"customer_care_calls", "weight_grams"}.issubset(df.columns):
        df["avg_delivery_time"] = (
            2.5 + df["customer_care_calls"] * 0.3 + df["weight_grams"] / 5000
        ).round(2)
        logger.info("Feature added: avg_delivery_time")
    return df


def add_priority_shipping_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Flag: high importance + cost above 75th percentile."""
    if {"product_importance", "product_cost"}.issubset(df.columns):
        threshold = df["product_cost"].quantile(0.75)
        df["priority_shipping_flag"] = (
            (df["product_importance"] >= 1) & (df["product_cost"] >= threshold)
        ).astype(int)
        logger.info("Feature added: priority_shipping_flag")
    return df


def add_discount_effectiveness(df: pd.DataFrame) -> pd.DataFrame:
    """Ratio of discount to product cost — higher = more aggressive discount."""
    if {"discount_offered", "product_cost"}.issubset(df.columns):
        df["discount_effectiveness"] = (
            df["discount_offered"] / (df["product_cost"] + 1e-9)
        ).round(4)
        logger.info("Feature added: discount_effectiveness")
    return df


def add_weight_category(df: pd.DataFrame) -> pd.DataFrame:
    """Bucket weight into Low / Medium / Heavy / Very Heavy."""
    if "weight_grams" in df.columns:
        df["weight_category"] = pd.cut(
            df["weight_grams"],
            bins=[0, 2000, 4000, 6000, np.inf],
            labels=[0, 1, 2, 3],   # encoded for ML
        ).astype(int)
        logger.info("Feature added: weight_category")
    return df


def add_customer_loyalty_score(df: pd.DataFrame) -> pd.DataFrame:
    """Combines rating + prior purchases into a loyalty score."""
    if {"customer_rating", "prior_purchases"}.issubset(df.columns):
        r_norm = df["customer_rating"] / df["customer_rating"].max()
        p_norm = df["prior_purchases"] / (df["prior_purchases"].max() + 1e-9)
        df["customer_loyalty_score"] = (0.5 * r_norm + 0.5 * p_norm).round(4)
        logger.info("Feature added: customer_loyalty_score")
    return df


# ─── Pipeline ────────────────────────────────────────────────────────────────
FEATURE_FUNCTIONS = [
    add_delivery_delay_days,
    add_shipping_efficiency_score,
    add_warehouse_load_score,
    add_customer_order_frequency,
    add_avg_delivery_time,
    add_priority_shipping_flag,
    add_discount_effectiveness,
    add_weight_category,
    add_customer_loyalty_score,
]


def run_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("=" * 50)
    logger.info("STARTING FEATURE ENGINEERING")
    logger.info("=" * 50)
    before_cols = set(df.columns)

    for fn in FEATURE_FUNCTIONS:
        df = fn(df)

    new_cols = set(df.columns) - before_cols
    logger.info(f"Feature engineering complete. {len(new_cols)} new features added:")
    for c in sorted(new_cols):
        logger.info(f"  + {c}")

    # Save feature list
    with open("outputs/feature_list.txt", "w") as f:
        f.write("ALL FEATURES AFTER ENGINEERING\n" + "="*50 + "\n")
        for col in df.columns:
            marker = "NEW" if col in new_cols else "   "
            f.write(f"  [{marker}] {col}\n")

    return df


if __name__ == "__main__":
    import preprocessing as pp
    df = pp.load_data(pp.RAW_DATA_PATH)
    df = pp.rename_columns(df)
    df = pp.handle_missing_values(df)
    df = pp.remove_duplicates(df)
    df = pp.convert_dtypes(df)
    df, encoders = pp.encode_categoricals(df)
    df = run_feature_engineering(df)
    print(df.head())
    print(f"\nFinal shape: {df.shape}")
