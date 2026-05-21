"""
train_cnn.py -- Phase 3 (IMPROVED): CNN Training with proper MobileNetV2 fine-tuning
Module 3 | CNN Parcel Damage Detection
Improvements:
  - MobileNetV2 native preprocessing
  - Cosine LR decay after warm-up
  - Unfreeze top-50 layers for fine-tuning
  - Class-weight balancing
  - Stronger augmentation (via augment.py)
  - Epochs = 50 + early stopping
  - BatchNormalization + Dropout in custom head
  - L2 regularization
"""
import os, json, time, shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
load_dotenv()

import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (EarlyStopping, ModelCheckpoint,
                                         ReduceLROnPlateau, LambdaCallback)
from tensorflow.keras.optimizers import Adam
from sklearn.utils.class_weight import compute_class_weight

from utils import (get_logger, save_fig, save_json, banner, Timer,
                   MODEL_DIR, IMG_SIZE, BATCH_SIZE, SEED,
                   DARK_BG, ACCENT, BLUE, GREEN, RED, ORANGE)
from augment import get_data_generators

logger = get_logger("train_cnn")

# ── Hyperparameters ───────────────────────────────────────────────────────────
EPOCHS    = int(os.getenv("EPOCHS", 50))
LR_HEAD   = float(os.getenv("LEARNING_RATE", 1e-4))   # frozen-base phase
LR_FT     = LR_HEAD / 10                               # fine-tune phase
DROPOUT   = float(os.getenv("DROPOUT_RATE", 0.4))
IMG_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
L2_REG    = 1e-4
UNFREEZE  = 50   # top N layers to unfreeze for fine-tuning


# ══════════════════════════════════════════════════════
# MODEL 1: Custom CNN (baseline)
# ══════════════════════════════════════════════════════
def build_custom_cnn() -> tf.keras.Model:
    reg = regularizers.l2(L2_REG)
    model = models.Sequential([
        layers.Input(shape=IMG_SHAPE),
        layers.Conv2D(32, 3, activation="relu", padding="same", kernel_regularizer=reg),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),

        layers.Conv2D(64, 3, activation="relu", padding="same", kernel_regularizer=reg),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),

        layers.Conv2D(128, 3, activation="relu", padding="same", kernel_regularizer=reg),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),

        layers.Conv2D(256, 3, activation="relu", padding="same", kernel_regularizer=reg),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling2D(),

        layers.Dense(256, activation="relu", kernel_regularizer=reg),
        layers.BatchNormalization(),
        layers.Dropout(DROPOUT),
        layers.Dense(128, activation="relu", kernel_regularizer=reg),
        layers.Dropout(DROPOUT / 2),
        layers.Dense(1, activation="sigmoid", name="output"),
    ], name="CustomCNN")

    model.compile(
        optimizer=Adam(LR_HEAD),
        loss="binary_crossentropy",
        metrics=["accuracy",
                 tf.keras.metrics.Precision(name="precision"),
                 tf.keras.metrics.Recall(name="recall"),
                 tf.keras.metrics.AUC(name="auc")],
    )
    return model


# ══════════════════════════════════════════════════════
# MODEL 2: MobileNetV2 (IMPROVED transfer learning)
# ══════════════════════════════════════════════════════
def build_mobilenet_improved() -> tf.keras.Model:
    """
    MobileNetV2 base + improved classification head:
    GlobalAvgPool → Dense(512, BN, relu) → Dropout →
    Dense(256, BN, relu) → Dropout → Dense(1, sigmoid)
    """
    base = MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights="imagenet")
    base.trainable = False   # frozen initially

    inputs = tf.keras.Input(shape=IMG_SHAPE)
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)

    x = layers.Dense(512, kernel_regularizer=regularizers.l2(L2_REG))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(DROPOUT)(x)

    x = layers.Dense(256, kernel_regularizer=regularizers.l2(L2_REG))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(DROPOUT / 2)(x)

    outputs = layers.Dense(1, activation="sigmoid", name="output")(x)
    model   = tf.keras.Model(inputs, outputs, name="MobileNetV2_Improved")

    model.compile(
        optimizer=Adam(LR_HEAD),
        loss="binary_crossentropy",
        metrics=["accuracy",
                 tf.keras.metrics.Precision(name="precision"),
                 tf.keras.metrics.Recall(name="recall"),
                 tf.keras.metrics.AUC(name="auc")],
    )
    return model


def unfreeze_mobilenet(model: tf.keras.Model, n: int = UNFREEZE, lr: float = LR_FT):
    """Unfreeze top N layers of the base for fine-tuning."""
    base = model.layers[1]
    base.trainable = True
    for layer in base.layers[:-n]:
        layer.trainable = False
    trainable_count = sum(1 for l in base.layers if l.trainable)
    logger.info(f"Fine-tune: {trainable_count}/{len(base.layers)} base layers unfrozen")
    model.compile(
        optimizer=Adam(lr),
        loss="binary_crossentropy",
        metrics=["accuracy",
                 tf.keras.metrics.Precision(name="precision"),
                 tf.keras.metrics.Recall(name="recall"),
                 tf.keras.metrics.AUC(name="auc")],
    )


# ── Callbacks ─────────────────────────────────────────────────────────────────
def get_callbacks(tag: str, patience_es: int = 10, patience_lr: int = 5) -> list:
    ckpt = os.path.join(MODEL_DIR, f"best_{tag}.keras")
    return [
        EarlyStopping(monitor="val_accuracy", patience=patience_es,
                      restore_best_weights=True, verbose=1, mode="max"),
        ModelCheckpoint(ckpt, monitor="val_accuracy", save_best_only=True,
                        verbose=0, mode="max"),
        ReduceLROnPlateau(monitor="val_loss", factor=0.4, patience=patience_lr,
                          min_lr=1e-8, verbose=1),
    ]


# ── Class weights ──────────────────────────────────────────────────────────────
def get_class_weights(train_gen) -> dict:
    labels = train_gen.classes
    classes = np.unique(labels)
    weights = compute_class_weight("balanced", classes=classes, y=labels)
    cw = dict(zip(classes.tolist(), weights.tolist()))
    logger.info(f"Class weights: {cw}")
    return cw


# ── Plot history ──────────────────────────────────────────────────────────────
def plot_history(histories: list, labels: list, name: str):
    """Overlay multiple training histories for comparison."""
    colors = [ACCENT, BLUE, GREEN, ORANGE]
    fig, axes = plt.subplots(1, 2, figsize=(16, 5), facecolor=DARK_BG)
    fig.suptitle(f"Training History — {name}", fontsize=14, color="white", fontweight="bold")

    for i, (hist, label) in enumerate(zip(histories, labels)):
        col   = colors[i % len(colors)]
        col2  = colors[(i + 1) % len(colors)]
        ep    = range(1, len(hist["loss"]) + 1)
        # Loss
        axes[0].plot(ep, hist["loss"],     color=col,  lw=2, label=f"{label} Train")
        axes[0].plot(ep, hist["val_loss"], color=col,  lw=2, linestyle="--", alpha=0.7,
                     label=f"{label} Val")
        # Accuracy
        axes[1].plot(ep, hist["accuracy"],     color=col,  lw=2, label=f"{label} Train")
        axes[1].plot(ep, hist["val_accuracy"], color=col,  lw=2, linestyle="--", alpha=0.7,
                     label=f"{label} Val")

    for ax, title, ylabel in [(axes[0], "Loss", "Binary Crossentropy"),
                               (axes[1], "Accuracy", "Accuracy")]:
        ax.set_title(title, color="white", fontsize=12)
        ax.set_xlabel("Epoch", color="white")
        ax.set_ylabel(ylabel, color="white")
        ax.legend(fontsize=9, ncol=2)
        ax.grid(True, alpha=0.2)

    plt.tight_layout()
    save_fig(f"04_training_history_{name.lower().replace(' ','_')}")


# ── Train single model ────────────────────────────────────────────────────────
def train_model(model, tag: str, train_gen, val_gen,
                class_weights=None, epochs=EPOCHS,
                patience_es=10) -> tuple:
    banner(f"TRAINING: {tag}")
    logger.info(f"Params: {model.count_params():,}")

    with Timer() as t:
        hist_obj = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=get_callbacks(tag, patience_es),
            class_weight=class_weights,
            verbose=1,
        )

    hist = hist_obj.history
    best_val_acc = max(hist["val_accuracy"])
    logger.info(f"Done in {t.elapsed}s | best_val_acc={best_val_acc:.4f}")

    path = os.path.join(MODEL_DIR, f"cnn_{tag.lower().replace(' ','_')}.keras")
    model.save(path)

    meta = {
        "tag": tag, "epochs": len(hist["loss"]),
        "best_val_acc":  round(float(best_val_acc), 4),
        "final_val_loss":round(float(hist["val_loss"][-1]), 5),
        "final_val_acc": round(float(hist["val_accuracy"][-1]), 4),
        "best_val_auc":  round(float(max(hist.get("val_auc", [0]))), 4),
        "training_time": t.elapsed, "model_path": path,
    }
    save_json(meta, f"training_meta_{tag.lower().replace(' ','_')}.json", "outputs")
    return hist, meta


# ── Main training pipeline ────────────────────────────────────────────────────
def run_training():
    banner("MODULE 3 — IMPROVED CNN TRAINING")

    train_gen, val_gen, test_gen, class_indices = get_data_generators()
    if train_gen.samples == 0:
        logger.error("No training images. Run preprocessing.py first.")
        return {}

    # Save class indices
    idx_path = os.path.join(MODEL_DIR, "class_indices.json")
    with open(idx_path, "w") as f:
        json.dump(class_indices, f, indent=2)

    class_weights = get_class_weights(train_gen)
    all_results   = {}

    # ── Model 1: Custom CNN ──────────────────────────────────────────────────
    cnn = build_custom_cnn()
    hist_cnn, meta_cnn = train_model(
        cnn, "custom_cnn", train_gen, val_gen,
        class_weights=class_weights, epochs=EPOCHS, patience_es=8
    )
    all_results["custom_cnn"] = meta_cnn

    # ── Model 2a: MobileNetV2 — frozen base ──────────────────────────────────
    mobile = build_mobilenet_improved()
    hist_phA, meta_phA = train_model(
        mobile, "mobilenet_phase_a", train_gen, val_gen,
        class_weights=class_weights, epochs=min(20, EPOCHS), patience_es=6
    )
    all_results["mobilenet_phase_a"] = meta_phA

    # ── Model 2b: MobileNetV2 — fine-tune top-50 layers ─────────────────────
    banner("MobileNetV2 FINE-TUNING (top-50 layers)")
    unfreeze_mobilenet(mobile, n=UNFREEZE, lr=LR_FT)
    hist_ft, meta_ft = train_model(
        mobile, "mobilenet_finetuned", train_gen, val_gen,
        class_weights=class_weights, epochs=EPOCHS, patience_es=12
    )
    all_results["mobilenet_finetuned"] = meta_ft

    # ── Comparison chart ─────────────────────────────────────────────────────
    plot_history(
        [hist_cnn, hist_phA, hist_ft],
        ["Custom CNN", "MobileNet Phase A", "MobileNet Fine-Tuned"],
        "All Models Comparison"
    )

    # ── Select best ──────────────────────────────────────────────────────────
    best_tag = max(all_results, key=lambda k: all_results[k]["best_val_acc"])
    best_acc = all_results[best_tag]["best_val_acc"]
    src = all_results[best_tag]["model_path"]
    dst = os.path.join(MODEL_DIR, "best_model.keras")
    shutil.copy2(src, dst)
    logger.info(f"Best model: {best_tag} (val_acc={best_acc}) -> {dst}")

    save_json(all_results, "all_training_results.json", "outputs")

    banner("TRAINING COMPLETE")
    for k, v in all_results.items():
        star = " ★ BEST" if k == best_tag else ""
        print(f"  {k:<30}: best_val_acc={v['best_val_acc']:.4f}{star}")

    return all_results


if __name__ == "__main__":
    run_training()
