"""
app.py -- Phase 6: Flask REST API for Damage Detection
Module 3 | CNN Parcel Damage Detection
Intelligent Logistics & E-Commerce Hub

Endpoints:
  GET  /
  GET  /health
  POST /api/v3/detect-damage
"""

import os, json, time
from datetime import datetime
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
load_dotenv()

from utils import get_logger
from predict import load_model_once, predict_single, preprocess_image

logger = get_logger("app")

app   = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

HOST  = os.getenv("FLASK_HOST",  "0.0.0.0")
PORT  = int(os.getenv("FLASK_PORT", 5002))
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# Pre-load model at startup
try:
    load_model_once()
    logger.info("Model pre-loaded successfully.")
    MODEL_READY = True
except Exception as e:
    logger.warning(f"Model not loaded at startup: {e}")
    MODEL_READY = False


# ── Root ──────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "module":      "Module 3 — CNN Parcel Damage Detection",
        "version":     "1.0.0",
        "model_ready": MODEL_READY,
        "endpoints": {
            "GET  /health":              "Service health check",
            "POST /api/v3/detect-damage": "Upload image for damage detection",
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }), 200


# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":      "ok" if MODEL_READY else "degraded",
        "model_ready": MODEL_READY,
        "module":      "Module 3 — CNN Parcel Damage Detection",
        "timestamp":   datetime.utcnow().isoformat() + "Z",
    }), 200 if MODEL_READY else 503


# ── Detect Damage ─────────────────────────────────────────────────────────────
@app.route("/api/v3/detect-damage", methods=["POST"])
def detect_damage():
    """
    Accepts:
      - multipart/form-data  with field 'image' (file upload)
      - application/json     with field 'image_path' (local path, dev mode)

    Returns:
      {
        "prediction":     "Damaged" | "Non Damaged",
        "confidence":     0.97,
        "damage_prob":    0.97,
        "class_index":    1,
        "response_time_ms": 38,
        "timestamp":      "..."
      }
    """
    if not MODEL_READY:
        return jsonify({
            "error": "Model not loaded. Run train_cnn.py first.",
            "hint":  "POST /api/v3/detect-damage requires a trained model."
        }), 503

    t_start = time.time()

    # ── File upload ──────────────────────────────────────────────────────────
    if "image" in request.files:
        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        allowed_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
        ext = os.path.splitext(file.filename.lower())[1]
        if ext not in allowed_exts:
            return jsonify({
                "error": f"Unsupported file type: {ext}",
                "allowed": list(allowed_exts)
            }), 415

        try:
            img_bytes = file.read()
            result    = predict_single(img_bytes=img_bytes)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Inference failed", "detail": str(e)}), 500

    # ── JSON path (dev/internal) ──────────────────────────────────────────────
    elif request.is_json:
        body      = request.get_json()
        img_path  = body.get("image_path", "")
        if not img_path or not os.path.isfile(img_path):
            return jsonify({"error": f"Image not found: {img_path}"}), 404
        try:
            result = predict_single(img_path=img_path)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Inference failed", "detail": str(e)}), 500

    else:
        return jsonify({
            "error": "Send image as multipart/form-data (field: 'image') "
                     "or JSON with 'image_path'."
        }), 400

    response_ms = round((time.time() - t_start) * 1000, 1)
    return jsonify({
        "prediction":       result["prediction"],
        "confidence":       result["confidence"],
        "damage_prob":      result["damage_prob"],
        "class_index":      result["class_index"],
        "response_time_ms": response_ms,
        "timestamp":        datetime.utcnow().isoformat() + "Z",
    }), 200


# ── Error handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Max 16MB."}), 413

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ── Request size limit ────────────────────────────────────────────────────────
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024   # 16 MB


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"Starting Flask Damage Detection API on {HOST}:{PORT}")
    logger.info("Endpoints:")
    logger.info("  GET  /")
    logger.info("  GET  /health")
    logger.info("  POST /api/v3/detect-damage")
    app.run(host=HOST, port=PORT, debug=DEBUG)
