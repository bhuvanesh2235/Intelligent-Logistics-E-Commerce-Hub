"""
download_dataset.py -- Download E-Commerce Shipping Dataset via kagglehub
"""
import os, sys, shutil, json

# ── 1. Kaggle credentials ────────────────────────────────────────────────────
KAGGLE_API_TOKEN = "KGAT_12e84ef733d3a83b04a86d9a6ce2fe81"
KAGGLE_USERNAME  = "yashch05"

kaggle_dir  = os.path.join(os.path.expanduser("~"), ".kaggle")
kaggle_json = os.path.join(kaggle_dir, "kaggle.json")
os.makedirs(kaggle_dir, exist_ok=True)

os.environ["KAGGLE_KEY"]      = KAGGLE_API_TOKEN
os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME

with open(kaggle_json, "w") as f:
    json.dump({"username": KAGGLE_USERNAME, "key": KAGGLE_API_TOKEN}, f)
try:
    os.chmod(kaggle_json, 0o600)
except Exception:
    pass

print(f"[OK] Kaggle credentials written to {kaggle_json}")

# ── 2. Download dataset ───────────────────────────────────────────────────────
import kagglehub

DATASET_ID = "yashch05/e-com-shipping-dataset"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"[>>] Downloading dataset: {DATASET_ID} ...")
path = kagglehub.dataset_download(DATASET_ID)
print(f"[OK] Downloaded to cache: {path}")

# ── 3. Copy CSVs to data/raw/ ─────────────────────────────────────────────────
csv_files = []
for root, dirs, files in os.walk(path):
    for fname in files:
        if fname.lower().endswith(".csv"):
            src = os.path.join(root, fname)
            dst = os.path.join(OUTPUT_DIR, fname)
            shutil.copy2(src, dst)
            csv_files.append(dst)
            print(f"[OK] Copied: {fname} --> {dst}")

if not csv_files:
    print("[!!] No CSV files found. Listing all downloaded files:")
    for root, dirs, files in os.walk(path):
        for fname in files:
            print(f"     {os.path.join(root, fname)}")
    sys.exit(1)

# ── 4. Preview ────────────────────────────────────────────────────────────────
import pandas as pd

main_csv = csv_files[0]
df = pd.read_csv(main_csv)
print(f"\n[INFO] Dataset: {os.path.basename(main_csv)}")
print(f"       Shape  : {df.shape}")
print(f"       Columns: {list(df.columns)}")
print(f"\n{df.head(3).to_string()}")

# ── 5. Save as expected filename ──────────────────────────────────────────────
expected = os.path.join(OUTPUT_DIR, "ecommerce_shipping.csv")
if not os.path.exists(expected):
    shutil.copy2(main_csv, expected)
    print(f"\n[OK] Also saved as: ecommerce_shipping.csv")

print("\n[DONE] Dataset ready! Run: python preprocessing.py")
