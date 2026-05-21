"""
train_lstm.py -- Phase 3: LSTM Model Architecture & Training
Module 2 | Intelligent Logistics & E-Commerce Hub
"""
import os, time
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"   # suppress TF info logs
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import (EarlyStopping, ModelCheckpoint,
                                         ReduceLROnPlateau, TensorBoard)
from tensorflow.keras.optimizers import Adam

from utils import get_logger, save_fig, MODEL_DIR, OUTPUT_DIR, save_json
from utils import ACCENT, BLUE, GREEN, RED, DARK_BG
from sequence_builder import build_sequences_for_task

load_dotenv()
logger = get_logger("train_lstm")

# ── Hyperparameters ───────────────────────────────────────────────────────────
EPOCHS       = int(os.getenv("EPOCHS",        60))
BATCH_SIZE   = int(os.getenv("BATCH_SIZE",    32))
UNITS_1      = int(os.getenv("LSTM_UNITS_1", 128))
UNITS_2      = int(os.getenv("LSTM_UNITS_2",  64))
DROPOUT      = float(os.getenv("DROPOUT",    0.2))
LR           = float(os.getenv("LEARNING_RATE", 0.001))


# ── Model Builder ─────────────────────────────────────────────────────────────
def build_lstm_model(lookback: int, n_features: int = 1) -> tf.keras.Model:
    """
    Deep LSTM architecture:
        Input(lookback, n_features)
        LSTM(128, return_sequences=True) + Dropout
        LSTM(64)                         + Dropout
        Dense(32, relu)
        Dense(1)
    """
    model = Sequential([
        Input(shape=(lookback, n_features)),
        LSTM(UNITS_1, return_sequences=True, name="lstm_1"),
        Dropout(DROPOUT, name="dropout_1"),
        LSTM(UNITS_2, return_sequences=False, name="lstm_2"),
        Dropout(DROPOUT, name="dropout_2"),
        Dense(32, activation="relu", name="dense_1"),
        Dense(1,  activation="linear", name="output"),
    ], name="LogisticsLSTM")

    model.compile(optimizer=Adam(learning_rate=LR), loss="mse",
                  metrics=["mae"])
    model.summary(print_fn=logger.info)
    return model


# ── Callbacks ─────────────────────────────────────────────────────────────────
def get_callbacks(task: str) -> list:
    ckpt_path = os.path.join(MODEL_DIR, f"best_{task}.keras")
    return [
        EarlyStopping(monitor="val_loss", patience=12, restore_best_weights=True,
                      verbose=1),
        ModelCheckpoint(ckpt_path, monitor="val_loss", save_best_only=True,
                        verbose=0),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=6,
                          min_lr=1e-6, verbose=1),
    ]


# ── Training ──────────────────────────────────────────────────────────────────
def train(task: str = "sales") -> dict:
    logger.info("=" * 55)
    logger.info(f"TRAINING LSTM FOR TASK: {task.upper()}")
    logger.info("=" * 55)

    seqs = build_sequences_for_task(task)
    X_train, X_val = seqs["X_train"], seqs["X_val"]
    y_train, y_val = seqs["y_train"], seqs["y_val"]
    lookback = seqs["lookback"]

    model = build_lstm_model(lookback, n_features=1)

    t0 = time.time()
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=get_callbacks(task),
        verbose=1,
    )
    elapsed = round(time.time() - t0, 2)
    logger.info(f"Training complete in {elapsed}s | epochs={len(history.epoch)}")

    # Save full model
    model_path = os.path.join(MODEL_DIR, f"lstm_{task}.keras")
    model.save(model_path)
    logger.info(f"Model saved: {model_path}")

    # Plot & save loss curve
    _plot_loss(history, task)

    # Save training metadata
    meta = {
        "task":           task,
        "epochs_trained": len(history.epoch),
        "final_train_loss": float(round(history.history["loss"][-1],   6)),
        "final_val_loss":   float(round(history.history["val_loss"][-1], 6)),
        "final_train_mae":  float(round(history.history["mae"][-1],     4)),
        "final_val_mae":    float(round(history.history["val_mae"][-1],  4)),
        "training_time_s":  elapsed,
        "hyperparams": {
            "lstm_units_1": UNITS_1, "lstm_units_2": UNITS_2,
            "dropout": DROPOUT, "learning_rate": LR,
            "batch_size": BATCH_SIZE, "lookback": lookback,
        },
    }
    save_json(meta, f"training_meta_{task}.json")

    return {"model": model, "history": history, "seqs": seqs, "meta": meta}


# ── Loss Plot ─────────────────────────────────────────────────────────────────
def _plot_loss(history, task: str):
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=DARK_BG)
    epochs  = range(1, len(history.history["loss"]) + 1)
    ax.plot(epochs, history.history["loss"],     color=ACCENT, lw=2, label="Train Loss")
    ax.plot(epochs, history.history["val_loss"], color=BLUE,   lw=2, label="Val Loss", linestyle="--")
    ax.set_title(f"LSTM Training Loss — {task.title()} Forecasting",
                 fontsize=14, color="white", fontweight="bold")
    ax.set_xlabel("Epoch", color="white")
    ax.set_ylabel("MSE Loss", color="white")
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    save_fig(f"loss_curve_{task}")


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for task in ["sales", "shipments"]:
        result = train(task)
        print(f"\n[{task.upper()}] Training summary:")
        for k, v in result["meta"].items():
            if k != "hyperparams":
                print(f"  {k:<25}: {v}")
