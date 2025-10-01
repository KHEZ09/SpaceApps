import os
import json
from flask import Flask, render_template, request, jsonify
from model import Predictor

app = Flask(__name__)
predictor = Predictor()  # loads model if exists or uses fallback

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/predict", methods=["POST"])
def api_predict():
    payload = request.json or {}
    lat = payload.get("lat", 4.7110)   # Bogotá default lat
    lon = payload.get("lon", -74.0721) # Bogotá default lon
    hours = payload.get("hours", 24)

    # predictor returns dict: { "aq_index": int, "pm25": float, "confidence": float, "explanation": str }
    result = predictor.get_prediction(lat, lon, hours)
    return jsonify(result)

@app.route("/api/advice", methods=["POST"])
def api_advice():
    payload = request.json or {}
    aq = payload.get("aq_index")       # e.g., 1-5 scale or pm2.5 value
    pm25 = payload.get("pm25")
    # simple rule engine for advice; predictor already gives some text, but provide structured advice
    advice = []
    if pm25 is None:
        advice.append("No PM2.5 value available.")
    else:
        if pm25 > 150:
            advice.append("Alerta: PM2.5 muy alta — evita salir, usa mascarilla N95 si sales.")
        elif pm25 > 55:
            advice.append("Calidad pobre: reduce actividad física al aire libre.")
        elif pm25 > 12:
            advice.append("Moderada: personas sensibles deben tomar precauciones.")
        else:
            advice.append("Buena: aire seguro para la mayoría de la población.")

    # add a short personalized tip
    advice.append("Consejo: cierra ventanas si hay picos y evita quemas/fuegos al exterior.")
    return jsonify({"advice": advice})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
