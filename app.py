from flask import Flask, render_template, request, redirect
from monitor import check_site
from database import load_sites, save_sites
import threading
import time

app = Flask(__name__)

@app.route("/")
def index():
    sites = load_sites()
    return render_template("index.html", sites=sites)

@app.route("/add", methods=["POST"])
def add_site():
    url = request.form["url"]
    sites = load_sites()
    if url not in sites:
        sites.append(url)
        save_sites(sites)
    return redirect("/")

@app.route("/check")
def check_all():
    sites = load_sites()
    for site in sites:
        check_site(site)
    return redirect("/")

def background_monitor():
    while True:
        sites = load_sites()
        for site in sites:
            check_site(site)
        time.sleep(300)  # cada 5 minutos

threading.Thread(target=background_monitor, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)