from flask import Flask, render_template, request, jsonify
from monitor import check_site
from database import load_sites, save_sites
import threading
import time

app = Flask(__name__)

# ---------------------------
# Rutas principales
# ---------------------------
@app.route("/")
def index():
    sites = load_sites()
    return render_template("index.html", sites=sites)

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
    """
    Endpoint AJAX que devuelve JSON:
    {"status": "ok" | "fail", "message": "..."}
    """
    url = request.json.get("url")
    if not url:
        return jsonify({"status": "fail", "message": "URL no proporcionada"}), 400
    ok = check_site(url)
    return jsonify({"status": "ok" if ok else "fail", "message": "Online" if ok else "Fallido"})

# ---------------------------
# Monitoreo automático cada 5 min
# ---------------------------
def background_monitor():
    while True:
        sites = load_sites()
        for site in sites:
            check_site(site)
        time.sleep(300)  # 5 min

threading.Thread(target=background_monitor, daemon=True).start()

# ---------------------------
# Arranque
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)