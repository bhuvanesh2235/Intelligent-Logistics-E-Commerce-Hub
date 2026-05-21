"""
augment.py -- Phase 2 (IMPROVED): Data Augmentation with MobileNetV2 preprocessing
Module 3 | CNN Parcel Damage Detection
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
from utils import (get_logger, save_fig, IMG_SIZE, BATCH_SIZE, SEED,
                   DARK_BG, ACCENT, BLUE, GREEN)

logger = get_logger("augment")

TRAIN_DIR = os.getenv("DATA_TRAIN_DIR", "data/train")
VAL_DIR   = os.getenv("DATA_VAL_DIR",   "data/val")
TEST_DIR  = os.getenv("DATA_TEST_DIR",  "data/test")


def get_data_generators(train_dir=TRAIN_DIR, val_dir=VAL_DIR, test_dir=TEST_DIR,
                         img_size=IMG_SIZE, batch_size=BATCH_SIZE):
    """
    IMPROVED: Uses MobileNetV2 native preprocessing + strong augmentation.
    train_gen  → augmented, MobileNetV2 scaled (-1, 1)
    val/test   → only MobileNetV2 preprocessing, no augmentation
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    # Strong augmentation for training
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=30,
        zoom_range=0.25,
        width_shift_range=0.15,
        height_shift_range=0.15,
        horizontal_flip=True,
        vertical_flip=False,
        brightness_range=[0.75, 1.25],
        shear_range=10,
        fill_mode="nearest",
    )

    # Evaluation generators: only MobileNetV2 preprocessing
    eval_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    train_gen = train_datagen.flow_from_directory(
        train_dir, target_size=(img_size, img_size),
        batch_size=batch_size, class_mode="binary",
        shuffle=True, seed=SEED,
    )
    val_gen = eval_datagen.flow_from_directory(
        val_dir, target_size=(img_size, img_size),
        batch_size=batch_size, class_mode="binary", shuffle=False,
    )
    test_gen = eval_datagen.flow_from_directory(
        test_dir, target_size=(img_size, img_size),
        batch_size=batch_size, class_mode="binary", shuffle=False,
    )

    logger.info(f"Train: {train_gen.samples} | Val: {val_gen.samples} | Test: {test_gen.samples}")
    logger.info(f"Class indices: {train_gen.class_indices}")
    return train_gen, val_gen, test_gen, train_gen.class_indices


def plot_augmentation_preview(train_dir=TRAIN_DIR, img_size=IMG_SIZE):
    """Visualise original + augmented images with labels."""
    from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

    classes = [d for d in os.listdir(train_dir)
               if os.path.isdir(os.path.join(train_dir, d))]
    if not classes:
        return

    cls_dir = os.path.join(train_dir, classes[0])
    imgs    = [f for f in os.listdir(cls_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
    if not imgs:
        return

    src = os.path.join(cls_dir, imgs[0])
    img = load_img(src, target_size=(img_size, img_size))
    x   = img_to_array(img).reshape((1,) + img_to_array(img).shape)

    aug_gen = ImageDataGenerator(
        rotation_range=30, zoom_range=0.25,
        width_shift_range=0.15, height_shift_range=0.15,
        horizontal_flip=True, brightness_range=[0.7, 1.3],
        shear_range=10, fill_mode="nearest",
    )

    n_aug = 7
    fig, axes = plt.subplots(2, n_aug + 1, figsize=(20, 6), facecolor=DARK_BG)
    fig.suptitle(f"Augmentation Preview — {classes[0].replace('_',' ').title()} class",
                 fontsize=13, color="white", fontweight="bold")

    for row in range(2):
        if row == 0:
            axes[row][0].imshow(img)
            axes[row][0].set_title("Original", color=GREEN, fontsize=9)
        else:
            axes[row][0].axis("off")
        axes[row][0].axis("off") if row == 1 else None

        aug_iter = aug_gen.flow(x, batch_size=1)
        for col in range(1, n_aug + 1):
            aug_img = next(aug_iter)[0].astype("uint8")
            axes[row][col].imshow(aug_img)
            axes[row][col].set_title(f"Aug #{(row)*n_aug + col}", color=ACCENT, fontsize=8)
            axes[row][col].axis("off")

    plt.tight_layout()
    save_fig("03_augmentation_preview")
    logger.info("Augmentation preview saved.")


if __name__ == "__main__":
    train_gen, val_gen, test_gen, class_indices = get_data_generators()
    plot_augmentation_preview()
    print(f"Generators ready. Classes: {class_indices}")
