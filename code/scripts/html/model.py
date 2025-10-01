import os, json
import numpy as np
import joblib
from datetime import datetime, timedelta
import requests

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

class Predictor:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print("Loaded model from", MODEL_PATH)
            except Exception as e:
                print("Could not load model:", e)
                self.model = None

    def fetch_openweather_air(self, lat, lon, api_key):
        # optional helper: if user supplies OpenWeather key in env var OPENWEATHER_API
        if not api_key:
            return None
        url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
        try:
            r = requests.get(url, timeout=6)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    def fetch_openaq_latest(self, lat, lon, radius_km=50):
        # Placeholder: recommend using OpenAQ API (no key) for ground stations
        # Implementation left as TODO — for hackathon, you can call OpenAQ REST endpoint from here.
        return None

    def get_prediction(self, lat, lon, hours=24):
        # 1) Try to collect realtime features (OpenWeather) if key provided
        openweather_key = os.environ.get("OPENWEATHER_API")
        obs = self.fetch_openweather_air(lat, lon, openweather_key) if openweather_key else None

        # 2) Build feature vector (very simple): use latest pm2_5 if available
        if obs:
            try:
                pm25 = obs["list"][0]["components"].get("pm2_5")
            except Exception:
                pm25 = None
        else:
            pm25 = None

        # If model available, use it; otherwise fallback heuristic
        if self.model and pm25 is not None:
            # model expects a vector, adjust as your training
            X = np.array([[pm25]])
            pred_pm25 = float(self.model.predict(X)[0])
            conf = 0.7
            explanation = "Modelo RF entrenado sobre datos históricos (fallback if low confidence)."
        else:
            # fallback naive persistence + small decay: predict same pm25 or a small change
            if pm25 is not None:
                pred_pm25 = float(pm25 * (1.0 + 0.05))  # +5% crude
                conf = 0.45
                explanation = "Predicción heurística: valor actual escalado (mientras modelo no esté disponible)."
            else:
                # no data at all → synthetic demo values for UI
                pred_pm25 = 25.0
                conf = 0.2
                explanation = "Valor por defecto (demo). Añade API keys o un modelo para predicciones reales."

        # convert to a simple AQI-like index (1-5) for quick display (very simple buckets)
        if pred_pm25 <= 12:
            aqi_idx = 1
        elif pred_pm25 <= 35.4:
            aqi_idx = 2
        elif pred_pm25 <= 55.4:
            aqi_idx = 3
        elif pred_pm25 <= 150.4:
            aqi_idx = 4
        else:
            aqi_idx = 5

        return {
            "location": {"lat": lat, "lon": lon},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pm25": round(pred_pm25, 2),
            "aq_index": aqi_idx,
            "confidence": round(conf, 2),
            "explanation": explanation
        }
