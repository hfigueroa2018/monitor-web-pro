from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS
from metrics import uptime_range, incidents_range, response_time_stats
from uptime import uptime_percent
from monitor import check_site
from database import load_sites, save_sites
import json
import os

app = Flask(__name__)
CORS(app)

# ---------- PÁGINA PRINCIPAL ----------
@app.route("/")
def index():
    return render_template("index.html")

# ---------- LISTAR SITIOS ----------
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

# ---------- AÑADIR SITIO (CORREGIDO: guardar ANTES de chequear) ----------
@app.route("/add", methods=["POST"])
def add_site():
    try:
        url = (request.form.get("url") or
               (request.json and request.json.get("url")))
        if not url:
            abort(400, description="URL requerida")

        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        sites = load_sites()
        if url in sites:
            return jsonify({"status": "ok", "message": "Sitio ya existe"}), 200

        # 1. Guardar primero
        sites.append(url)
        save_sites(sites)

        # 2. Chequear después (opcional)
        check_site(url)

        return jsonify({"status": "ok", "message": "Sitio añadido y probado"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        abort(500, description=str(e))

# ---------- CONFIGURAR FRECUENCIA ----------
@app.route("/config", methods=["POST"])
def config():
    freq = int(request.form.get("freq", 60))
    action = request.form.get("action", "stop")
    config_data = {"freq": freq, "action": action}
    with open("config.json", "w") as f:
        json.dump(config_data, f)
    return jsonify({"status": "success", "action": action, "freq": freq})

# ---------- PROBAR SITIO AHORA ----------
@app.route("/check", methods=["POST"])
def check_site_now():
    data = request.get_json()
    if not data or "url" not in data:
        abort(400, description="URL no proporcionada")
    url = data["url"]
    ok = check_site(url)
    return jsonify({"status": "ok" if ok else "fail", "message": "Online" if ok else "Fallido"})

# ---------- MÉTRICAS ----------
@app.route("/metrics/<path:url>")
def metrics_data(url):
    from urllib.parse import unquote
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

# ---------- HANDLERS DE ERROR ----------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# ---------- ARRANQUE ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)