"""
eda.py -- Exploratory Data Analysis (adapted for 50K fulfillment dataset)
"""
import os, logging, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # non-interactive backend for Windows
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CHART_DIR = "outputs/charts"
os.makedirs(CHART_DIR, exist_ok=True)

DARK_BG = "#1a1a2e"
PANEL   = "#16213e"
ACCENT  = "#e94560"
BLUE    = "#00b4d8"
GREEN   = "#7bed9f"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL,
    "axes.edgecolor": "#0f3460", "axes.labelcolor": "white",
    "xtick.color": "white", "ytick.color": "white",
    "text.color": "white", "grid.color": "#0f3460",
    "font.family": "DejaVu Sans",
})


def _save(name):
    p = os.path.join(CHART_DIR, f"{name}.png")
    plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    logger.info(f"Chart saved: {p}")


# 1. Dataset Overview
def dataset_overview(df):
    print("\n" + "="*60)
    print(f"Shape : {df.shape}")
    print(f"Cols  : {list(df.columns)}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nMissing:\n{df.isnull().sum()}")
    print(f"\nStats:\n{df.describe().T.round(2).to_string()}")


# 2. Delivery Status Distribution
def plot_delivery_status(df):
    raw = pd.read_csv("data/raw/ecommerce_shipping.csv")
    if "Delivery_Status" not in raw.columns: return
    counts = raw["Delivery_Status"].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor=DARK_BG)
    fig.suptitle("Delivery Status Distribution", fontsize=15, color="white", fontweight="bold")
    axes[0].pie(counts.values, labels=counts.index, autopct="%1.1f%%",
                colors=[BLUE, ACCENT], textprops={"color": "white"},
                wedgeprops={"edgecolor": DARK_BG})
    axes[0].set_title("Proportion", color="white")
    axes[1].bar(counts.index, counts.values, color=[BLUE, ACCENT], edgecolor=DARK_BG)
    axes[1].set_title("Count", color="white")
    for bar, v in zip(axes[1].patches, counts.values):
        axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+100,
                     f"{v:,}", ha="center", color="white", fontsize=11)
    plt.tight_layout(); _save("01_delivery_status")


# 3. Delivery Days Distribution
def plot_delivery_days(df):
    raw = pd.read_csv("data/raw/ecommerce_shipping.csv")
    if "Delivery_Days" not in raw.columns: return
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=DARK_BG)
    for status, color, label in [("Delivered", BLUE, "Delivered"), ("Delayed", ACCENT, "Delayed")]:
        subset = raw[raw["Delivery_Status"] == status]["Delivery_Days"].dropna()
        ax.hist(subset, bins=30, alpha=0.75, color=color, label=label, edgecolor=DARK_BG)
    ax.set_title("Delivery Days by Status", fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Delivery Days", color="white")
    ax.set_ylabel("Count", color="white")
    ax.legend(); plt.tight_layout(); _save("02_delivery_days")


# 4. Shipping Mode Analysis
def plot_shipping_mode(df):
    raw = pd.read_csv("data/raw/ecommerce_shipping.csv")
    if "Shipping_Mode" not in raw.columns: return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor=DARK_BG)
    fig.suptitle("Shipping Mode Analysis", fontsize=15, color="white", fontweight="bold")
    mode_counts = raw["Shipping_Mode"].value_counts()
    axes[0].bar(mode_counts.index, mode_counts.values,
                color=[BLUE, ACCENT, GREEN], edgecolor=DARK_BG)
    axes[0].set_title("Orders by Mode", color="white")
    for bar, v in zip(axes[0].patches, mode_counts.values):
        axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
                     f"{v:,}", ha="center", color="white", fontsize=10)

    ontime = raw.groupby("Shipping_Mode")["Delivery_Status"].apply(
        lambda x: (x == "Delivered").mean() * 100).sort_values()
    axes[1].barh(ontime.index, ontime.values, color=BLUE, edgecolor=DARK_BG)
    axes[1].set_title("On-Time Rate by Mode (%)", color="white")
    axes[1].set_xlabel("%", color="white")
    for bar in axes[1].patches:
        axes[1].text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                     f"{bar.get_width():.1f}%", va="center", color="white")
    plt.tight_layout(); _save("03_shipping_mode")


# 5. Region Analysis
def plot_region(df):
    raw = pd.read_csv("data/raw/ecommerce_shipping.csv")
    if "Customer_Region" not in raw.columns: return
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=DARK_BG)
    counts = raw["Customer_Region"].value_counts()
    colors = [BLUE, ACCENT, GREEN, "#ffa502", "#a29bfe"]
    bars = ax.bar(counts.index, counts.values, color=colors[:len(counts)], edgecolor=DARK_BG)
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
                f"{v:,}", ha="center", color="white", fontsize=11)
    ax.set_title("Orders by Customer Region", fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Region", color="white")
    ax.set_ylabel("Orders", color="white")
    plt.tight_layout(); _save("04_region_analysis")


# 6. Shipping Cost Distribution
def plot_shipping_cost(df):
    raw = pd.read_csv("data/raw/ecommerce_shipping.csv")
    if "Shipping_Cost" not in raw.columns: return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor=DARK_BG)
    fig.suptitle("Shipping Cost Analysis", fontsize=15, color="white", fontweight="bold")
    axes[0].hist(raw["Shipping_Cost"].dropna(), bins=40, color=BLUE, edgecolor=DARK_BG, alpha=0.85)
    axes[0].set_title("Cost Distribution", color="white")
    axes[0].set_xlabel("Cost", color="white")

    avg_cost = raw.groupby("Shipping_Mode")["Shipping_Cost"].mean().sort_values()
    axes[1].barh(avg_cost.index, avg_cost.values, color=ACCENT, edgecolor=DARK_BG)
    axes[1].set_title("Avg Cost by Mode", color="white")
    axes[1].set_xlabel("Avg Cost", color="white")
    plt.tight_layout(); _save("05_shipping_cost")


# 7. Product Category Analysis
def plot_category(df):
    raw = pd.read_csv("data/raw/ecommerce_shipping.csv")
    if "Product_Category" not in raw.columns: return
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=DARK_BG)
    counts = raw["Product_Category"].value_counts()
    colors = [BLUE, ACCENT, GREEN, "#ffa502", "#a29bfe", "#fd79a8"]
    bars = ax.bar(counts.index, counts.values, color=colors[:len(counts)], edgecolor=DARK_BG)
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+30,
                f"{v:,}", ha="center", color="white", fontsize=10)
    ax.set_title("Orders by Product Category", fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Category", color="white")
    ax.set_ylabel("Orders", color="white")
    plt.xticks(rotation=15)
    plt.tight_layout(); _save("06_product_category")


# 8. Correlation Heatmap (processed)
def plot_correlation(df):
    num_df = df.select_dtypes(include=[np.number]).drop(columns=["order_id"], errors="ignore")
    if num_df.shape[1] < 2: return
    corr = num_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=DARK_BG)
    sns.heatmap(corr, mask=mask, cmap=sns.diverging_palette(220, 20, as_cmap=True),
                center=0, annot=True, fmt=".2f", annot_kws={"size": 6},
                ax=ax, linewidths=0.5, linecolor=DARK_BG)
    ax.set_title("Feature Correlation Heatmap", fontsize=14, color="white", fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout(); _save("07_correlation_heatmap")


# 9. Engineered Features Overview
def plot_engineered(df):
    feats = ["delivery_delay_days", "shipping_efficiency_score",
             "warehouse_load_score", "avg_delivery_time",
             "cost_per_day", "priority_shipping_flag"]
    avail = [f for f in feats if f in df.columns]
    if not avail: return
    colors = ["#e94560", "#00b4d8", "#7bed9f", "#ffa502", "#a29bfe", "#fd79a8"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), facecolor=DARK_BG)
    fig.suptitle("Engineered Features Overview", fontsize=15, color="white", fontweight="bold")
    axes = axes.flatten()
    for i, feat in enumerate(avail[:6]):
        axes[i].hist(df[feat].dropna(), bins=30, color=colors[i], edgecolor=DARK_BG, alpha=0.85)
        axes[i].set_title(feat.replace("_", " ").title(), color="white", fontsize=10)
        axes[i].set_ylabel("Freq", color="white", fontsize=8)
    for j in range(len(avail), 6):
        axes[j].set_visible(False)
    plt.tight_layout(); _save("08_engineered_features")


# ── Run All ───────────────────────────────────────────────────────────────────
def run_eda(df: pd.DataFrame):
    logger.info("Starting EDA...")
    dataset_overview(df)
    plot_delivery_status(df)
    plot_delivery_days(df)
    plot_shipping_mode(df)
    plot_region(df)
    plot_shipping_cost(df)
    plot_category(df)
    plot_correlation(df)
    plot_engineered(df)
    logger.info(f"All charts saved --> {CHART_DIR}")


if __name__ == "__main__":
    processed = "data/processed/cleaned_dataset.csv"
    if not os.path.exists(processed):
        print("Run preprocessing.py first!")
        exit(1)
    df = pd.read_csv(processed)
    run_eda(df)
