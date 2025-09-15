from flask import Flask, render_template, request, jsonify, abort
from metrics import uptime_range, incidents_range, response_time_stats
from uptime import uptime_percent, record_check
from monitor import check_site
from database import load_sites, save_sites
import json
import os
import time

app = Flask(__name__)

# -----------------------------
# Ruta principal: Dashboard
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------
# Ruta: Lista de sitios
# -----------------------------
@app.route("/sites")
def get_sites():
    if os.path.exists("sites.json"):
        try:
            with open("sites.json", "r") as f:
                sites = json.load(f)
            return jsonify(sites)
        except Exception as e:
            abort(500, description=f"Error leyendo sitios: {str(e)}")
    return jsonify([])

# -----------------------------
# Ruta: Configurar frecuencia
# -----------------------------
@app.route("/config", methods=["POST"])
def config():
    freq = int(request.form.get("freq", 60))
    action = request.form.get("action", "stop")
    # Guardamos en archivo temporal (puedes usar base de datos después)
    config_data = {"freq": freq, "action": action}
    with open("config.json", "w") as f:
        json.dump(config_data, f)
    return jsonify({"status": "success", "action": action, "freq": freq})

# -----------------------------
# Ruta: Probar sitio ahora
# -----------------------------
@app.route("/check", methods=["POST"])
def check_site_now():
    data = request.get_json()
    if not data or "url" not in data:
        abort(400, description="URL no proporcionada")
    url = data["url"]
    ok = check_site(url)
    return jsonify({"status": "ok" if ok else "fail", "message": "Online" if ok else "Fallido"})

# -----------------------------
# Ruta: Métricas históricas
# -----------------------------
@app.route("/metrics/<path:url>")
def metrics_data(url):
    from urllib.parse import unquote
    try:
        url = unquote(url)
        days = int(request.args.get("days", 1))
        if days <= 0 or days > 365:
            days = 1
        return jsonify({
            "uptime": uptime_range(url, days),
            "incidents": incidents_range(url, days),
            "response": response_time_stats(url, days),
            "uptime_percent": uptime_percent(url)
        })
    except Exception as e:
        abort(500, description=f"Error en métricas: {str(e)}")

# -----------------------------
# Error handlers
# -----------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# -----------------------------
# Arranque
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)