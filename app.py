from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS
from metrics import uptime_range, incidents_range, response_time_stats
from uptime import uptime_percent
from monitor import check_site
from database import load_sites, save_sites
import json
import os
import threading
import time
from scheduler import run_monitor

app = Flask(__name__)
CORS(app)

# Iniciar el scheduler en un hilo separado cuando se inicia la aplicación
monitor_thread = threading.Thread(target=run_monitor, daemon=True)
monitor_thread.start()
print("[APP] Scheduler iniciado en segundo plano")

# ---------- RAÍZ ----------
@app.route("/")
def index():
    return render_template("index.html")

# ---------- CONFIG (frecuencia) ----------
def get_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return int(cfg.get("freq", 60))
    except Exception:
        return 60

@app.route("/config", methods=["POST"])
def config():
    freq = int(request.form.get("freq", 60))
    action = request.form.get("action", "stop")
    cfg = {"freq": freq, "action": action}
    with open("config.json", "w") as f:
        json.dump(cfg, f)
    return jsonify({"status": "success", "action": action, "freq": freq})

@app.route("/config", methods=["GET"])
def config_json():
    return jsonify({"freq": get_config()})

# ---------- SITIOS ----------
@app.route("/sites")
def get_sites():
    return jsonify(load_sites())

# ---------- AÑADIR SITIO ----------
@app.route("/add", methods=["POST"])
def add_site():
    try:
        url = (request.form.get("url") or (request.json and request.json.get("url")))
        if not url: abort(400, description="URL requerida")
        url = url.strip()
        if not url.startswith(("http://", "https://")): url = "https://" + url
        sites = load_sites()
        if any(s["url"] == url for s in sites):
            return jsonify({"status": "ok", "message": "Sitio ya existe"}), 200
        sites.append({"url": url, "chat_id": None})  # chat_id opcional
        save_sites(sites)
        check_site(url)
        return jsonify({"status": "ok", "message": "Sitio añadido y probado"})
    except Exception as e:
        import traceback; traceback.print_exc()
        abort(500, description=str(e))

# ---------- CHEQUEO ----------
@app.route("/check", methods=["POST"])
def check_site_now():
    data = request.get_json()
    if not data or "url" not in data:
        abort(400, description="URL no proporcionada")
    from urllib.parse import unquote
    url = unquote(data["url"]).strip()
    ok = check_site(url)
    return jsonify({"status": "ok" if ok else "fail", "message": "Online" if ok else "Fallido"})

# ---------- MÉTRICAS ----------
@app.route("/metrics/<path:url>")
def metrics_data(url):
    from urllib.parse import unquote
    url = unquote(url)
    days = int(request.args.get("days", 1))
    if days <= 0 or days > 365: days = 1
    return jsonify({
        "uptime": uptime_range(url, days),
        "incidents": incidents_range(url, days),
        "response": response_time_stats(url, days),
        "uptime_percent": uptime_percent(url)
    })

# ---------- ERRORES ----------
@app.errorhandler(404)
def not_found(error): return jsonify({"error": "Recurso no encontrado"}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({"error": "Error interno"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)