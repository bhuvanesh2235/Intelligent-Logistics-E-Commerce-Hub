"""
utils.py -- Shared utilities for Module 2 LSTM Forecasting
"""
import os, logging, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
MODEL_DIR  = os.getenv("MODEL_DIR",  "models")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
CHART_DIR  = os.getenv("CHART_DIR",  "outputs/charts")

for d in [MODEL_DIR, OUTPUT_DIR, CHART_DIR, "data"]:
    os.makedirs(d, exist_ok=True)

# ── Logging ───────────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        fh = logging.FileHandler(os.path.join(OUTPUT_DIR, "forecasting.log"), encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(sh)
        logger.addHandler(fh)
    return logger

# ── Dark plot style ───────────────────────────────────────────────────────────
DARK_BG = "#1a1a2e"
PANEL   = "#16213e"
ACCENT  = "#6c63ff"
BLUE    = "#00b4d8"
GREEN   = "#00d4aa"
RED     = "#e94560"
ORANGE  = "#ffa502"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL,
    "axes.edgecolor": "#2a2a4a", "axes.labelcolor": "white",
    "xtick.color": "white", "ytick.color": "white",
    "text.color": "white", "grid.color": "#2a2a4a",
    "font.family": "DejaVu Sans", "legend.facecolor": PANEL,
    "legend.edgecolor": "#2a2a4a",
})

def save_fig(name: str):
    path = os.path.join(CHART_DIR, f"{name}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    logging.getLogger("utils").info(f"Chart saved: {path}")
    return path

# ── Trend detector ────────────────────────────────────────────────────────────
def detect_trend(values: list) -> str:
    if len(values) < 3:
        return "stable"
    arr = np.array(values, dtype=float)
    slope = np.polyfit(range(len(arr)), arr, 1)[0]
    pct   = abs(slope) / (np.mean(arr) + 1e-9)
    if pct > 0.02:
        return "upward" if slope > 0 else "downward"
    return "stable"

# ── Save JSON artifact ────────────────────────────────────────────────────────
def save_json(obj: dict, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    return path

# ── Moving average ────────────────────────────────────────────────────────────
def moving_average(arr: np.ndarray, window: int = 7) -> np.ndarray:
    return np.convolve(arr, np.ones(window) / window, mode="valid")
