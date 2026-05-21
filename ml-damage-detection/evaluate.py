"""
evaluate.py -- Phase 4: Model Evaluation & Visual Analytics
Module 3 | CNN Parcel Damage Detection
"""

import os, json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
load_dotenv()

import tensorflow as tf
from sklearn.metrics import (confusion_matrix, classification_report,
                              roc_curve, auc, f1_score,
                              precision_score, recall_score, accuracy_score)
from PIL import Image

from utils import (get_logger, save_fig, save_json, banner, Timer,
                   MODEL_DIR, REPORT_DIR, CHART_DIR,
                   IMG_SIZE, BATCH_SIZE, DARK_BG,
                   ACCENT, BLUE, GREEN, RED, ORANGE, PANEL)

logger = get_logger("evaluate")

TRAIN_DIR = os.getenv("DATA_TRAIN_DIR", "data/train")
VAL_DIR   = os.getenv("DATA_VAL_DIR",   "data/val")
TEST_DIR  = os.getenv("DATA_TEST_DIR",  "data/test")


def _get_simple_test_gen(test_dir=TEST_DIR, img_size=IMG_SIZE, batch_size=BATCH_SIZE):
    """
    Simple 1/255 rescaling test generator.
    Used when best_model.keras was trained with rescale=1/255 (not MobileNetV2 preprocess_input).
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    gen = ImageDataGenerator(rescale=1.0 / 255)
    tg  = gen.flow_from_directory(
        test_dir, target_size=(img_size, img_size),
        batch_size=batch_size, class_mode="binary", shuffle=False,
    )
    # Also build val gen for completeness
    val_gen = ImageDataGenerator(rescale=1.0 / 255).flow_from_directory(
        VAL_DIR, target_size=(img_size, img_size),
        batch_size=batch_size, class_mode="binary", shuffle=False,
    )
    logger.info(f"Test samples: {tg.samples} | Class indices: {tg.class_indices}")
    return tg, tg.class_indices



# ── Load best model ───────────────────────────────────────────────────────────
def load_best_model() -> tf.keras.Model:
    path = os.path.join(MODEL_DIR, "best_model.keras")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Run train_cnn.py first. Expected: {path}")
    model = tf.keras.models.load_model(path)
    logger.info(f"Loaded model: {path}")
    return model


# ── Generate predictions ──────────────────────────────────────────────────────
def get_predictions(model, test_gen) -> tuple:
    """Returns (y_true, y_pred_prob, y_pred_class)."""
    logger.info("Running inference on test set...")
    with Timer() as t:
        probs = model.predict(test_gen, verbose=1).flatten()
    logger.info(f"Inference time: {t.elapsed}s for {len(probs)} samples")

    y_true  = test_gen.classes
    y_pred  = (probs >= 0.5).astype(int)
    return y_true, probs, y_pred


# ── Metrics ───────────────────────────────────────────────────────────────────
def compute_metrics(y_true, y_pred, y_prob) -> dict:
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec  = recall_score(y_true, y_pred, zero_division=0)
    f1   = f1_score(y_true, y_pred, zero_division=0)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)

    metrics = {
        "accuracy":  round(float(acc),     4),
        "precision": round(float(prec),    4),
        "recall":    round(float(rec),     4),
        "f1_score":  round(float(f1),      4),
        "roc_auc":   round(float(roc_auc), 4),
    }
    logger.info(f"Metrics: {metrics}")
    return metrics, fpr, tpr, roc_auc


# ── Confusion Matrix ──────────────────────────────────────────────────────────
def plot_confusion_matrix(y_true, y_pred, class_names: list):
    cm   = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(7, 6), facecolor=DARK_BG)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names,
                ax=ax, linewidths=0.5, linecolor=DARK_BG,
                annot_kws={"size": 16, "color": "white"})
    ax.set_title("Confusion Matrix", fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Predicted", color="white", fontsize=12)
    ax.set_ylabel("Actual",    color="white", fontsize=12)
    ax.tick_params(colors="white")
    plt.tight_layout()
    save_fig("05_confusion_matrix")


# ── ROC Curve ─────────────────────────────────────────────────────────────────
def plot_roc_curve(fpr, tpr, roc_auc: float):
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=DARK_BG)
    ax.plot(fpr, tpr, color=ACCENT, lw=2.5,
            label=f"ROC Curve (AUC = {roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], color="white", lw=1, linestyle="--", alpha=0.5,
            label="Random Classifier")
    ax.fill_between(fpr, tpr, alpha=0.08, color=ACCENT)
    ax.set_title("ROC Curve — Damage Detection",
                 fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("False Positive Rate", color="white")
    ax.set_ylabel("True Positive Rate",  color="white")
    ax.legend(fontsize=12); ax.grid(True, alpha=0.2)
    save_fig("06_roc_curve")


# ── Prediction Samples Grid ───────────────────────────────────────────────────
def plot_prediction_samples(model, test_gen, class_indices: dict, n: int = 8):
    """Show sample correct and incorrect predictions."""
    inv_map = {v: k for k, v in class_indices.items()}
    all_paths = test_gen.filepaths
    all_true  = test_gen.classes

    probs = model.predict(test_gen, verbose=0).flatten()
    preds = (probs >= 0.5).astype(int)

    correct   = [i for i in range(len(preds)) if preds[i] == all_true[i]]
    incorrect = [i for i in range(len(preds)) if preds[i] != all_true[i]]

    def _grid(indices, title, fname):
        n_show = min(n, len(indices))
        if n_show == 0:
            return
        fig, axes = plt.subplots(2, n_show // 2 + n_show % 2,
                                 figsize=(16, 5), facecolor=DARK_BG)
        fig.suptitle(title, fontsize=13, color="white", fontweight="bold")
        axes = axes.flatten()
        for ax_i, idx in enumerate(indices[:n_show]):
            try:
                img = Image.open(all_paths[idx]).resize((IMG_SIZE, IMG_SIZE))
                axes[ax_i].imshow(np.array(img))
            except Exception:
                axes[ax_i].imshow(np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8))
            true_label = inv_map.get(all_true[idx], str(all_true[idx]))
            pred_label = inv_map.get(preds[idx],   str(preds[idx]))
            conf       = probs[idx] if preds[idx] == 1 else 1 - probs[idx]
            color      = GREEN if preds[idx] == all_true[idx] else RED
            axes[ax_i].set_title(
                f"T:{true_label}\nP:{pred_label} ({conf:.0%})",
                color=color, fontsize=8
            )
            axes[ax_i].axis("off")
        for ax_i in range(n_show, len(axes)):
            axes[ax_i].set_visible(False)
        plt.tight_layout()
        save_fig(fname)

    import random
    random.shuffle(correct)
    random.shuffle(incorrect)
    _grid(correct[:n],   "Correct Predictions",   "07_correct_predictions")
    _grid(incorrect[:n], "Incorrect Predictions", "08_incorrect_predictions")


# ── Main evaluation ───────────────────────────────────────────────────────────
def run_evaluation():
    banner("MODULE 3 - MODEL EVALUATION")

    model = load_best_model()
    test_gen, class_indices = _get_simple_test_gen()

    if test_gen.samples == 0:
        logger.error("No test images. Run preprocessing.py first.")
        return {}

    class_names = list(class_indices.keys())
    y_true, y_prob, y_pred = get_predictions(model, test_gen)

    metrics, fpr, tpr, roc_auc = compute_metrics(y_true, y_pred, y_prob)

    # Charts
    plot_confusion_matrix(y_true, y_pred, class_names)
    plot_roc_curve(fpr, tpr, roc_auc)
    plot_prediction_samples(model, test_gen, class_indices)

    # Full classification report
    report_text = classification_report(
        y_true, y_pred,
        target_names=class_names,
        zero_division=0,
    )
    print(f"\n{'='*55}\n  CLASSIFICATION REPORT\n{'='*55}")
    print(report_text)

    report_path = os.path.join(REPORT_DIR, "classification_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Save metrics JSON
    full_results = {
        "metrics":    metrics,
        "class_names": class_names,
        "test_samples": int(len(y_true)),
        "model_path":  os.path.join(MODEL_DIR, "best_model.keras"),
        "report_path": report_path,
    }
    save_json(full_results, "evaluation_results.json", REPORT_DIR)

    banner("EVALUATION COMPLETE")
    print(f"  Accuracy : {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall   : {metrics['recall']:.4f}")
    print(f"  F1-Score : {metrics['f1_score']:.4f}")
    print(f"  ROC-AUC  : {metrics['roc_auc']:.4f}")
    print(f"  Charts saved to: {CHART_DIR}")

    return full_results


if __name__ == "__main__":
    run_evaluation()
