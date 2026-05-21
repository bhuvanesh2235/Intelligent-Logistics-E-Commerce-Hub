"""
preprocessing.py -- Phase 1: Dataset Download, Preprocessing & Split
Module 3 | CNN Parcel Damage Detection
Intelligent Logistics & E-Commerce Hub
"""

import os, sys, shutil, json, random
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dotenv import load_dotenv

load_dotenv()

from utils import (get_logger, save_fig, save_json, banner,
                   IMG_SIZE, SEED, CLASSES, CHART_DIR, REPORT_DIR,
                   DARK_BG, ACCENT, BLUE, GREEN, RED, ORANGE,
                   scan_images, is_valid_image, is_image_file)

logger = get_logger("preprocessing")
random.seed(SEED)
np.random.seed(SEED)

# ── Config ────────────────────────────────────────────────────────────────────
KAGGLE_TOKEN    = os.getenv("KAGGLE_API_TOKEN", "")
KAGGLE_USER     = os.getenv("KAGGLE_USERNAME",  "yashch05")
DATASET_ID      = os.getenv("DATASET_ID", "christianvorhemus/industrial-quality-control-of-packages")
RAW_DIR         = os.getenv("DATA_RAW_DIR",   "data/raw")
TRAIN_DIR       = os.getenv("DATA_TRAIN_DIR", "data/train")
VAL_DIR         = os.getenv("DATA_VAL_DIR",   "data/val")
TEST_DIR        = os.getenv("DATA_TEST_DIR",  "data/test")
TRAIN_SPLIT     = float(os.getenv("TRAIN_SPLIT", 0.70))
VAL_SPLIT       = float(os.getenv("VAL_SPLIT",   0.15))


# ── Phase 1a: Download Dataset ────────────────────────────────────────────────
def download_dataset() -> str:
    """Download Kaggle dataset using kagglehub and copy to data/raw/."""
    banner("PHASE 1a: DATASET DOWNLOAD")

    # Write credentials
    kaggle_dir  = os.path.join(os.path.expanduser("~"), ".kaggle")
    kaggle_json = os.path.join(kaggle_dir, "kaggle.json")
    os.makedirs(kaggle_dir, exist_ok=True)
    os.environ["KAGGLE_KEY"]      = KAGGLE_TOKEN
    os.environ["KAGGLE_USERNAME"] = KAGGLE_USER
    creds = {"username": KAGGLE_USER, "key": KAGGLE_TOKEN}
    with open(kaggle_json, "w") as f:
        json.dump(creds, f)
    try:
        os.chmod(kaggle_json, 0o600)
    except Exception:
        pass
    logger.info(f"Kaggle credentials written to {kaggle_json}")

    import kagglehub
    logger.info(f"Downloading dataset: {DATASET_ID}")
    path = kagglehub.dataset_download(DATASET_ID)
    logger.info(f"Downloaded to cache: {path}")

    # Copy all images to data/raw/ preserving subdirectory structure
    os.makedirs(RAW_DIR, exist_ok=True)
    copied = 0
    for root, dirs, files in os.walk(path):
        for fname in files:
            if is_image_file(fname):
                src = os.path.join(root, fname)
                rel  = os.path.relpath(root, path)   # e.g. 'damaged' or 'intact'
                dst_dir = os.path.join(RAW_DIR, rel)
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, fname)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                copied += 1

    logger.info(f"Total images copied to {RAW_DIR}: {copied}")
    return RAW_DIR


# ── Phase 1b: Discover Classes ────────────────────────────────────────────────
def discover_classes(raw_dir: str) -> dict:
    """
    Scan raw_dir and map directory names to class labels.
    Looks for 'damaged' and 'non_damaged' (or similar) subdirectories.
    Returns {class_label: [image_paths]}
    """
    banner("PHASE 1b: CLASS DISCOVERY")

    class_map = {}
    # Keyword mapping — covers this dataset and similar ones
    KEYWORD_MAP = {
        "damaged":     ["defect", "damage", "broken", "bad", "ng", "faulty", "fail"],
        "non_damaged": ["ok", "good", "normal", "non", "pass", "undamaged",
                        "intact", "healthy", "fine"],
    }
    # Walk one level deep
    for entry in os.scandir(raw_dir):
        if not entry.is_dir():
            continue
        name_lower = entry.name.lower().strip()
        label = None
        for canonical, keywords in KEYWORD_MAP.items():
            if any(kw in name_lower for kw in keywords):
                label = canonical
                break
        if label is None:
            label = name_lower.replace(" ", "_").replace("-", "_")

        imgs = [os.path.join(entry.path, f)
                for f in os.listdir(entry.path) if is_image_file(f)]
        if imgs:
            if label not in class_map:
                class_map[label] = []
            class_map[label].extend(imgs)
            logger.info(f"  Folder '{entry.name}' -> class '{label}': {len(imgs)} images")

    if not class_map:
        # Fallback: treat all images as one class and split manually
        all_imgs = scan_images(raw_dir)
        n = len(all_imgs)
        half = n // 2
        class_map["damaged"]     = all_imgs[:half]
        class_map["non_damaged"] = all_imgs[half:]
        logger.warning(f"No subdirectories found — split {n} images into 2 classes")

    return class_map


# ── Phase 1c: Validate & Resize Images ───────────────────────────────────────
def process_image(src_path: str, dst_path: str, size: int = IMG_SIZE) -> bool:
    """Resize and normalize image, save as JPEG. Returns True on success."""
    try:
        with Image.open(src_path) as img:
            img = img.convert("RGB")
            img = img.resize((size, size), Image.LANCZOS)
            img.save(dst_path, "JPEG", quality=95)
        return True
    except Exception as e:
        logger.debug(f"Skipping corrupt image {src_path}: {e}")
        return False


# ── Phase 1d: Train/Val/Test Split ────────────────────────────────────────────
def create_splits(class_map: dict) -> dict:
    """Split each class into train/val/test and copy processed images."""
    banner("PHASE 1c-d: PREPROCESSING & SPLITTING")

    stats = {"classes": {}, "total": {"train": 0, "val": 0, "test": 0, "skipped": 0}}

    for class_label, img_paths in class_map.items():
        random.shuffle(img_paths)
        n       = len(img_paths)
        n_train = int(n * TRAIN_SPLIT)
        n_val   = int(n * VAL_SPLIT)
        # test = remainder
        splits = {
            "train": img_paths[:n_train],
            "val":   img_paths[n_train:n_train + n_val],
            "test":  img_paths[n_train + n_val:],
        }

        counts = {}
        for split_name, paths in splits.items():
            dst_dir = os.path.join(f"data/{split_name}", class_label)
            os.makedirs(dst_dir, exist_ok=True)
            ok, skip = 0, 0
            for i, src in enumerate(paths):
                fname = f"{class_label}_{split_name}_{i:05d}.jpg"
                dst   = os.path.join(dst_dir, fname)
                if process_image(src, dst):
                    ok += 1
                else:
                    skip += 1
            counts[split_name] = ok
            stats["total"][split_name] += ok
            stats["total"]["skipped"]  += skip
            logger.info(f"  [{class_label}/{split_name}] saved={ok}, skipped={skip}")

        stats["classes"][class_label] = counts

    return stats


# ── Phase 1e: Charts ──────────────────────────────────────────────────────────
def plot_class_distribution(stats: dict):
    """Bar chart of class × split distribution."""
    classes = list(stats["classes"].keys())
    splits  = ["train", "val", "test"]
    colors  = [ACCENT, BLUE, GREEN]

    x = np.arange(len(classes))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=DARK_BG)
    for i, (split, color) in enumerate(zip(splits, colors)):
        vals = [stats["classes"][c].get(split, 0) for c in classes]
        bars = ax.bar(x + i * width, vals, width, label=split.title(),
                      color=color, edgecolor=DARK_BG)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 5, str(v),
                    ha="center", color="white", fontsize=9)

    ax.set_xticks(x + width)
    ax.set_xticklabels([c.replace("_", " ").title() for c in classes],
                       fontsize=12)
    ax.set_title("Dataset Class Distribution", fontsize=14,
                 color="white", fontweight="bold")
    ax.set_ylabel("Image Count", color="white")
    ax.legend(fontsize=11)
    ax.grid(True, axis="y", alpha=0.25)
    save_fig("01_class_distribution")


def plot_sample_grid(class_map: dict, n_per_class: int = 6):
    """Grid of sample images per class."""
    classes = list(class_map.keys())
    n_cols  = n_per_class
    n_rows  = len(classes)

    fig = plt.figure(figsize=(n_cols * 2.5, n_rows * 2.8), facecolor=DARK_BG)
    fig.suptitle("Sample Dataset Images", fontsize=14,
                 color="white", fontweight="bold", y=1.01)

    for row, cls in enumerate(classes):
        samples = random.sample(class_map[cls], min(n_per_class, len(class_map[cls])))
        for col, img_path in enumerate(samples):
            ax = fig.add_subplot(n_rows, n_cols, row * n_cols + col + 1)
            try:
                img = Image.open(img_path).convert("RGB").resize((112, 112))
                ax.imshow(np.array(img))
            except Exception:
                ax.imshow(np.zeros((112, 112, 3), dtype=np.uint8))
            ax.axis("off")
            if col == 0:
                ax.set_ylabel(cls.replace("_", "\n").title(),
                              color="white", fontsize=9, rotation=0,
                              labelpad=60, va="center")

    plt.tight_layout()
    save_fig("02_sample_images")


# ── Phase 1f: Summary Report ─────────────────────────────────────────────────
def generate_report(stats: dict, class_map: dict) -> str:
    report = {
        "module":         "Module 3 - CNN Damage Detection",
        "dataset":        DATASET_ID,
        "image_size":     f"{IMG_SIZE}x{IMG_SIZE}",
        "train_split":    TRAIN_SPLIT,
        "val_split":      VAL_SPLIT,
        "test_split":     round(1 - TRAIN_SPLIT - VAL_SPLIT, 2),
        "class_totals":   {c: len(v) for c, v in class_map.items()},
        "split_counts":   stats,
    }
    path = save_json(report, "dataset_summary.json", REPORT_DIR)
    logger.info(f"Report saved: {path}")
    return path


# ── Main Pipeline ─────────────────────────────────────────────────────────────
def run_preprocessing():
    banner("MODULE 3 - PREPROCESSING PIPELINE STARTED")

    # 1a. Download
    raw_dir = download_dataset()

    # 1b. Discover classes
    class_map = discover_classes(raw_dir)
    if not class_map:
        logger.error("No image classes found in dataset. Exiting.")
        sys.exit(1)

    logger.info(f"Classes found: {list(class_map.keys())}")
    logger.info(f"Total images : {sum(len(v) for v in class_map.values())}")

    # 1c–d. Split & preprocess
    stats = create_splits(class_map)

    # 1e. Charts
    plot_class_distribution(stats)
    plot_sample_grid(class_map)

    # 1f. Report
    generate_report(stats, class_map)

    # Summary
    banner("PREPROCESSING COMPLETE")
    print(f"  Classes     : {list(class_map.keys())}")
    print(f"  Train images: {stats['total']['train']}")
    print(f"  Val images  : {stats['total']['val']}")
    print(f"  Test images : {stats['total']['test']}")
    print(f"  Skipped     : {stats['total']['skipped']}")
    print(f"  Charts saved to: {CHART_DIR}")

    return class_map, stats


if __name__ == "__main__":
    run_preprocessing()
