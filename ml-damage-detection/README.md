# Module 3 — CNN Parcel Damage Detection

> **Intelligent Logistics & E-Commerce Hub** | Computer Vision pipeline for automated damaged package detection using deep learning.

![Module](https://img.shields.io/badge/Module-3%20--%20CNN%20Damage%20Detection-6c63ff?style=flat-square)
![Stack](https://img.shields.io/badge/Stack-TensorFlow%20%7C%20Flask%20%7C%20OpenCV-00d4aa?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-success?style=flat-square)

---

## Overview

This module implements an end-to-end Computer Vision pipeline for detecting damaged vs non-damaged shipping packages. It trains two CNN models (custom CNN + MobileNetV2 transfer learning) and exposes predictions via a production-ready Flask REST API.

---

## Folder Structure

```
ml-damage-detection/
├── data/
│   ├── raw/              # Downloaded Kaggle dataset
│   ├── processed/        # Intermediate processed images
│   ├── train/            # 70% split (damaged/ + non_damaged/)
│   ├── val/              # 15% split
│   └── test/             # 15% split
│
├── models/
│   ├── cnn_custom_cnn.keras         # Custom CNN model
│   ├── cnn_mobilenet_finetuned.keras # Fine-tuned MobileNetV2
│   ├── best_model.keras             # Best performing model
│   └── class_indices.json
│
├── outputs/
│   ├── charts/           # All visualisation PNGs
│   ├── reports/          # Evaluation JSON + text reports
│   └── predictions/      # Batch prediction results
│
├── preprocessing.py      # Phase 1 — download, resize, split
├── augment.py            # Phase 2 — ImageDataGenerators
├── train_cnn.py          # Phase 3 — model architecture + training
├── evaluate.py           # Phase 4 — metrics + charts
├── predict.py            # Phase 5 — single & batch inference
├── app.py                # Phase 6 — Flask REST API
├── utils.py              # Shared utilities
├── requirements.txt
├── .env
└── README.md
```

---

## Dataset

- **Source**: [Industrial Quality Control of Packages](https://www.kaggle.com/datasets/christianvorhemus/industrial-quality-control-of-packages)
- **Downloaded via**: `kagglehub`
- **Classes**: `damaged` / `non_damaged`
- **Image size**: Resized to 224×224 RGB

---

## Quick Start

### 1. Install Dependencies
```bash
cd ml-damage-detection
pip install -r requirements.txt
```

### 2. Run Full Pipeline
```bash
# Phase 1 — Download & Preprocess
python preprocessing.py

# Phase 2 — Verify augmentation
python augment.py

# Phase 3 — Train CNN models
python train_cnn.py

# Phase 4 — Evaluate
python evaluate.py

# Phase 5 — Predict single image
python predict.py data/test/damaged/some_image.jpg

# Phase 6 — Start Flask API
python app.py
```

---

## CNN Architecture

### Model 1: Custom CNN
```
Input(224, 224, 3)
  Conv2D(32)  + BatchNorm + MaxPool
  Conv2D(64)  + BatchNorm + MaxPool
  Conv2D(128) + BatchNorm + MaxPool
  Conv2D(256) + BatchNorm + GlobalAvgPool
  Dense(256) + Dropout(0.4)
  Dense(128) + Dropout(0.2)
  Dense(1, sigmoid)
```

### Model 2: MobileNetV2 Transfer Learning
```
MobileNetV2 (ImageNet weights, frozen)
  GlobalAveragePooling2D
  Dense(256) + Dropout(0.4)
  Dense(128) + Dropout(0.2)
  Dense(1, sigmoid)
  --- Fine-tuning: top 30 layers unfrozen ---
```

**Training Config:**

| Parameter       | Value           |
|-----------------|-----------------|
| Optimizer       | Adam            |
| Loss            | Binary Crossentropy |
| Metrics         | Acc, Precision, Recall, AUC |
| Early Stopping  | patience=8      |
| LR Scheduler    | ReduceLROnPlateau |
| Max Epochs      | 30              |
| Batch Size      | 32              |
| Image Size      | 224×224         |
| Augmentation    | rotation, zoom, flip, brightness, shift |

---

## Flask API

Base URL: `http://localhost:5002`

### GET `/`
Returns API info and model status.

### GET `/health`
```json
{ "status": "ok", "model_ready": true }
```

### POST `/api/v3/detect-damage`

**Option A — File Upload (multipart/form-data)**
```bash
curl -X POST http://localhost:5002/api/v3/detect-damage \
  -F "image=@package.jpg"
```

**Option B — JSON path (dev)**
```json
{ "image_path": "data/test/damaged/sample.jpg" }
```

**Response:**
```json
{
  "prediction":       "Damaged",
  "confidence":       0.97,
  "damage_prob":      0.97,
  "class_index":      1,
  "response_time_ms": 38,
  "timestamp":        "2025-05-18T15:30:00Z"
}
```

---

## Evaluation Metrics

| Metric     | Description                          |
|------------|--------------------------------------|
| Accuracy   | Overall correct predictions          |
| Precision  | Of predicted damaged, how many are?  |
| Recall     | Of actual damaged, how many caught?  |
| F1-Score   | Harmonic mean of precision & recall  |
| ROC-AUC    | Area under receiver operating curve  |

---

## Generated Charts

| Chart                           | Description                     |
|---------------------------------|---------------------------------|
| `01_class_distribution.png`     | Dataset split bar chart         |
| `02_sample_images.png`          | Sample image grid per class     |
| `03_augmentation_preview.png`   | Original + 7 augmented variants |
| `04_training_history_*.png`     | Loss + accuracy curves          |
| `05_confusion_matrix.png`       | True/false positive heatmap     |
| `06_roc_curve.png`              | ROC-AUC curve                   |
| `07_correct_predictions.png`    | Sample correct predictions      |
| `08_incorrect_predictions.png`  | Sample misclassifications       |

---

## Integration with Other Modules

| Module   | Integration Point                                      |
|----------|--------------------------------------------------------|
| Module 1 | Spring Boot backend calls `/api/v3/detect-damage`      |
| Module 2 | Damage rate fed into shipment demand forecasting       |
| Frontend | React admin dashboard displays damage detection results|

---

## Capstone Summary

| Module   | Feature                         | Status   |
|----------|---------------------------------|----------|
| Module 1 | Full-stack E-Commerce Platform  | Complete |
| Module 2 | LSTM Sales Forecasting          | Complete |
| Module 3 | CNN Parcel Damage Detection     | Complete |
