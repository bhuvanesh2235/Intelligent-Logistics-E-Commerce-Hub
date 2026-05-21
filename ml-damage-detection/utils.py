"""
utils.py -- Shared utilities for Module 3: CNN Damage Detection
Intelligent Logistics & E-Commerce Hub
"""
import os, logging, json, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dotenv import load_dotenv

load_dotenv()

# ── Directories ───────────────────────────────────────────────────────────────
MODEL_DIR  = os.getenv("MODEL_DIR",  "models")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
CHART_DIR  = os.getenv("CHART_DIR",  "outputs/charts")
REPORT_DIR = os.getenv("REPORT_DIR", "outputs/reports")

for d in [MODEL_DIR, OUTPUT_DIR, CHART_DIR, REPORT_DIR,
          "outputs/predictions", "data/raw", "data/processed"]:
    os.makedirs(d, exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────────────────
IMG_SIZE   = int(os.getenv("IMG_SIZE",   224))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
SEED       = int(os.getenv("SEED",       42))
CLASSES    = ["non_damaged", "damaged"]   # index 0 = non_damaged, 1 = damaged

# ── Dark theme ────────────────────────────────────────────────────────────────
DARK_BG = "#1a1a2e"
PANEL   = "#16213e"
ACCENT  = "#6c63ff"
BLUE    = "#00b4d8"
GREEN   = "#00d4aa"
RED     = "#e94560"
ORANGE  = "#ffa502"

plt.rcParams.update({
    "figure.facecolor": DARK_BG,
    "axes.facecolor":   PANEL,
    "axes.edgecolor":   "#2a2a4a",
    "axes.labelcolor":  "white",
    "xtick.color":      "white",
    "ytick.color":      "white",
    "text.color":       "white",
    "grid.color":       "#2a2a4a",
    "font.family":      "DejaVu Sans",
    "legend.facecolor": PANEL,
    "legend.edgecolor": "#2a2a4a",
})


# ── Logger ────────────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        fh = logging.FileHandler(
            os.path.join(OUTPUT_DIR, "damage_detection.log"), encoding="utf-8"
        )
        fh.setFormatter(fmt)
        logger.addHandler(sh)
        logger.addHandler(fh)
    return logger


# ── Chart saver ───────────────────────────────────────────────────────────────
def save_fig(name: str, dpi: int = 150) -> str:
    path = os.path.join(CHART_DIR, f"{name}.png")
    plt.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=DARK_BG)
    plt.close("all")
    logging.getLogger("utils").info(f"Chart saved: {path}")
    return path


# ── JSON helpers ──────────────────────────────────────────────────────────────
def save_json(obj: dict, filename: str, subdir: str = "outputs") -> str:
    path = os.path.join(subdir, filename)
    os.makedirs(subdir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    return path


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Timer context ─────────────────────────────────────────────────────────────
class Timer:
    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = round(time.time() - self._start, 2)


# ── Image validation ──────────────────────────────────────────────────────────
def is_valid_image(path: str) -> bool:
    """Check whether a file is a readable image."""
    try:
        from PIL import Image
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


# ── Supported extensions ──────────────────────────────────────────────────────
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def is_image_file(fname: str) -> bool:
    return os.path.splitext(fname.lower())[1] in IMAGE_EXTS


# ── Recursive image scanner ───────────────────────────────────────────────────
def scan_images(directory: str) -> list:
    """Return all image file paths under directory."""
    paths = []
    for root, _, files in os.walk(directory):
        for f in files:
            if is_image_file(f):
                paths.append(os.path.join(root, f))
    return paths


# ── Section banner ────────────────────────────────────────────────────────────
def banner(text: str, width: int = 55):
    line = "=" * width
    print(f"\n{line}\n  {text}\n{line}")
