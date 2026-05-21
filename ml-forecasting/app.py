"""
app.py -- Phase 6: Flask Forecasting API
Module 2 | Intelligent Logistics & E-Commerce Hub

Endpoints:
  GET  /health
  GET  /api/v2/info
  POST /api/v2/forecast/sales
  POST /api/v2/forecast/shipment-demand
  GET  /api/v2/forecast/sales/quick
  GET  /api/v2/forecast/shipments/quick
"""
import os, json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from dotenv import load_dotenv

load_dotenv()

from utils import get_logger
from predict import forecast_future, LOOKBACK, HORIZON

logger = get_logger("app")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

HOST  = os.getenv("FLASK_HOST", "0.0.0.0")
PORT  = int(os.getenv("FLASK_PORT", 5001))
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"


# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":    "ok",
        "module":    "Module 2 — LSTM Forecasting",
        "version":   "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }), 200


# ── Module Info ───────────────────────────────────────────────────────────────
@app.route("/api/v2/info", methods=["GET"])
def info():
    return jsonify({
        "module":      "LSTM Sales & Shipment Demand Forecasting",
        "models":      ["sales", "shipments"],
        "horizons":    [7, 14, 30],
        "lookback":    LOOKBACK,
        "description": "Recursive multi-step LSTM forecasting for logistics demand.",
        "endpoints": {
            "POST /api/v2/forecast/sales":            "Sales volume forecast",
            "POST /api/v2/forecast/shipment-demand":  "Shipment demand forecast",
            "GET  /api/v2/forecast/sales/quick":      "Quick 7-day sales forecast",
            "GET  /api/v2/forecast/shipments/quick":  "Quick 7-day shipment forecast",
        }
    }), 200


# ── Sales Forecast ────────────────────────────────────────────────────────────
@app.route("/api/v2/forecast/sales", methods=["POST"])
def forecast_sales():
    """
    Body (optional):
      {
        "horizon": 7,              // forecast days (1-90)
        "historical": [120, 135, ...] // custom last N values (optional)
      }
    """
    body    = request.get_json(silent=True) or {}
    horizon = int(body.get("horizon", HORIZON))
    horizon = max(1, min(horizon, 90))

    custom_window = None
    if "historical" in body:
        arr = np.array(body["historical"], dtype=float)
        if len(arr) >= 5:
            custom_window = arr

    try:
        result = forecast_future("sales", horizon=horizon, custom_window=custom_window)
        return jsonify(_format_response(result)), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e), "hint": "Run train_lstm.py first"}), 503
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Forecasting failed", "detail": str(e)}), 500


# ── Shipment Demand Forecast ──────────────────────────────────────────────────
@app.route("/api/v2/forecast/shipment-demand", methods=["POST"])
def forecast_shipment():
    body    = request.get_json(silent=True) or {}
    horizon = int(body.get("horizon", HORIZON))
    horizon = max(1, min(horizon, 90))

    custom_window = None
    if "historical" in body:
        arr = np.array(body["historical"], dtype=float)
        if len(arr) >= 5:
            custom_window = arr

    try:
        result = forecast_future("shipments", horizon=horizon, custom_window=custom_window)
        return jsonify(_format_response(result)), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e), "hint": "Run train_lstm.py first"}), 503
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Forecasting failed", "detail": str(e)}), 500


# ── Quick Endpoints (GET) ─────────────────────────────────────────────────────
@app.route("/api/v2/forecast/sales/quick", methods=["GET"])
def quick_sales():
    horizon = int(request.args.get("horizon", 7))
    try:
        result = forecast_future("sales", horizon=min(horizon, 30))
        return jsonify(_format_response(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v2/forecast/shipments/quick", methods=["GET"])
def quick_shipments():
    horizon = int(request.args.get("horizon", 7))
    try:
        result = forecast_future("shipments", horizon=min(horizon, 30))
        return jsonify(_format_response(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Response Formatter ────────────────────────────────────────────────────────
def _format_response(result: dict) -> dict:
    horizon   = result["forecast_days"]
    base_date = datetime.utcnow().date()
    dates     = [(base_date + timedelta(days=i+1)).isoformat() for i in range(horizon)]

    return {
        "status":        "success",
        "task":          result["task"],
        "forecast_days": horizon,
        "trend":         result["trend"],
        "avg_forecast":  result["avg_forecast"],
        "peak_day":      result["peak_day"],
        "peak_value":    result["peak_value"],
        "predictions":   result["predicted"],
        "lower_bound":   result["lower_bound"],
        "upper_bound":   result["upper_bound"],
        "dates":         dates,
        "chart_data": [
            {
                "date":  d,
                "value": v,
                "lower": l,
                "upper": u,
            }
            for d, v, l, u in zip(dates, result["predicted"],
                                   result["lower_bound"], result["upper_bound"])
        ],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


# ── Error Handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"Starting Flask Forecasting API on {HOST}:{PORT}")
    logger.info("Endpoints:")
    logger.info("  GET  /health")
    logger.info("  GET  /api/v2/info")
    logger.info("  POST /api/v2/forecast/sales")
    logger.info("  POST /api/v2/forecast/shipment-demand")
    logger.info("  GET  /api/v2/forecast/sales/quick?horizon=7")
    logger.info("  GET  /api/v2/forecast/shipments/quick?horizon=7")
    app.run(host=HOST, port=PORT, debug=DEBUG)
