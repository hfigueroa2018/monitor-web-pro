from flask import Flask, render_template, request, jsonify, redirect
from monitor import check_site
from database import load_sites, save_sites
from uptime import uptime_percent, total_uptime_str
import threading
import time

app = Flask(__name__)

# Frecuencia por defecto (segundos)
DEFAULT_FREQ = 60

# Variable global para controlar el hilo
current_freq = DEFAULT_FREQ
monitoring = False

# ---------------------------
# Rutas principales
# ---------------------------
@app.route("/")
def index():
    sites = load_sites()
    return render_template("index.html", sites=sites, freq=current_freq, monitoring=monitoring)

@app.route("/config", methods=["POST"])
def config():
    global current_freq, monitoring
    freq = int(request.form["freq"])
    action = request.form["action"]
    current_freq = freq
    if action == "start":
        monitoring = True
    elif action == "stop":
        monitoring = False
    return redirect("/")

@app.route("/add", methods=["POST"])
def add_site():
    url = request.form["url"].strip()
    if not url.startswith("http"):
        url = "https://" + url
    sites = load_sites()
    if url not in sites:
        sites.append(url)
        save_sites(sites)
    return redirect("/")

@app.route("/check", methods=["POST"])
def check_now():
    url = request.json.get("url")
    if not url:
        return jsonify({"status": "fail", "message": "URL no proporcionada"}), 400
    ok = check_site(url)
    return jsonify({"status": "ok" if ok else "fail", "message": "Online" if ok else "Fallido"})

@app.route("/uptime/<path:url>")
def uptime_data(url):
    from urllib.parse import unquote
    url = unquote(url)
    up = uptime_percent(url)
    total = total_uptime_str(url)
    return {
        "url": url,
        "uptime_percent": up,
        "total_uptime": total,
        "status": "up" if up == 100 else "down"
    }

# ---------------------------
# Monitoreo automático
# ---------------------------
def background_monitor():
    while True:
        if not monitoring:
            time.sleep(1)
            continue
        sites = load_sites()
        for site in sites:
            check_site(site)
        time.sleep(current_freq)

threading.Thread(target=background_monitor, daemon=True).start()

# ---------------------------
# Arranque
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)