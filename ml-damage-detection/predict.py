"""
predict.py -- Phase 5: Inference System
Module 3 | CNN Parcel Damage Detection
"""

import os, json, time
import numpy as np
from PIL import Image
from dotenv import load_dotenv

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
load_dotenv()

import tensorflow as tf

from utils import (get_logger, save_json, MODEL_DIR, IMG_SIZE,
                   is_image_file, CLASSES, banner)

logger = get_logger("predict")

# ── Singleton model loader ────────────────────────────────────────────────────
_MODEL       = None
_CLASS_IDX   = None


def load_model_once():
    global _MODEL, _CLASS_IDX
    if _MODEL is None:
        model_path = os.path.join(MODEL_DIR, "best_model.keras")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found: {model_path}. Run train_cnn.py first."
            )
        _MODEL = tf.keras.models.load_model(model_path)
        logger.info(f"Model loaded: {model_path}")

    if _CLASS_IDX is None:
        idx_path = os.path.join(MODEL_DIR, "class_indices.json")
        if os.path.exists(idx_path):
            with open(idx_path, "r") as f:
                _CLASS_IDX = json.load(f)
        else:
            _CLASS_IDX = {"non_damaged": 0, "damaged": 1}
        logger.info(f"Class indices: {_CLASS_IDX}")

    return _MODEL, _CLASS_IDX


# ── Preprocess single image ───────────────────────────────────────────────────
def preprocess_image(img_path: str = None,
                      img_bytes: bytes = None,
                      size: int = IMG_SIZE) -> np.ndarray:
    """Load and preprocess an image from path or raw bytes."""
    if img_bytes is not None:
        import io
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    elif img_path is not None:
        img = Image.open(img_path).convert("RGB")
    else:
        raise ValueError("Provide img_path or img_bytes")

    img   = img.resize((size, size), Image.LANCZOS)
    arr   = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)   # (1, H, W, 3)


# ── Single image prediction ───────────────────────────────────────────────────
def predict_single(img_path: str = None,
                    img_bytes: bytes = None) -> dict:
    """
    Returns:
        {
          "prediction":  "Damaged" | "Non Damaged",
          "confidence":  0.97,
          "class_index": 1,
          "inference_ms": 38
        }
    """
    model, class_idx = load_model_once()
    inv_map = {v: k for k, v in class_idx.items()}

    x = preprocess_image(img_path=img_path, img_bytes=img_bytes)

    t0   = time.time()
    prob = float(model.predict(x, verbose=0)[0][0])
    ms   = round((time.time() - t0) * 1000, 1)

    # prob is probability of the positive class (index 1)
    # Determine which index is "damaged"
    damaged_idx = class_idx.get("damaged", 1)
    if damaged_idx == 1:
        damage_prob = prob
    else:
        damage_prob = 1 - prob

    predicted_idx = 1 if damage_prob >= 0.5 else 0
    label         = inv_map.get(predicted_idx, CLASSES[predicted_idx])
    confidence    = damage_prob if predicted_idx == damaged_idx else 1 - damage_prob

    result = {
        "prediction":   label.replace("_", " ").title(),
        "confidence":   round(float(confidence), 4),
        "class_index":  predicted_idx,
        "damage_prob":  round(float(damage_prob), 4),
        "inference_ms": ms,
    }

    if img_path:
        result["image_path"] = img_path
        logger.info(
            f"[SINGLE] {os.path.basename(img_path)} -> "
            f"{result['prediction']} ({result['confidence']:.2%}) "
            f"in {ms}ms"
        )
    return result


# ── Batch folder prediction ───────────────────────────────────────────────────
def predict_batch(folder_path: str, save_results: bool = True) -> list:
    """
    Predict all images in a folder.
    Returns list of prediction dicts.
    """
    banner(f"BATCH PREDICTION: {folder_path}")
    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder not found: {folder_path}")

    image_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if is_image_file(f)
    ]

    if not image_files:
        logger.warning(f"No images found in {folder_path}")
        return []

    logger.info(f"Found {len(image_files)} images. Running batch inference...")
    results = []
    for img_path in image_files:
        try:
            res = predict_single(img_path=img_path)
            results.append(res)
        except Exception as e:
            logger.warning(f"Skipping {img_path}: {e}")

    # Summary
    n_damaged     = sum(1 for r in results if r["class_index"] == 1)
    n_non_damaged = len(results) - n_damaged
    summary = {
        "total":        len(results),
        "damaged":      n_damaged,
        "non_damaged":  n_non_damaged,
        "damage_rate":  round(n_damaged / max(len(results), 1), 4),
        "predictions":  results,
    }

    if save_results:
        out = os.path.join("outputs", "predictions", "batch_results.json")
        save_json(summary, "batch_results.json", "outputs/predictions")
        logger.info(f"Batch results saved: {out}")

    print(f"\n  Total images : {summary['total']}")
    print(f"  Damaged      : {summary['damaged']}")
    print(f"  Non-Damaged  : {summary['non_damaged']}")
    print(f"  Damage Rate  : {summary['damage_rate']:.1%}")
    return results


# ── CLI entry ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path_or_folder>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        predict_batch(target)
    elif os.path.isfile(target):
        result = predict_single(img_path=target)
        print(json.dumps(result, indent=2))
    else:
        print(f"Path not found: {target}")
        sys.exit(1)
