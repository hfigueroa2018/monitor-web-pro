# scheduler.py
import time
import json
import os
from monitor import check_site
from database import load_sites

CONFIG_FILE = "config.json"

def get_freq():
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        return int(cfg.get("freq", 60))
    except Exception as e:
        print("[SCHEDULER] Error leyendo config.json:", e)
        return 60  # valor por defecto

# Memoria en RAM: último estado por URL
last_status = {}

def run_monitor():
    while True:
        freq = get_freq()
        sites = load_sites()
        for site in sites:
            url = site["url"]
            print(f"[SCHEDULER] Revisando {url}")
            try:
                ok = check_site(url)
                status_key = "up" if ok else "down"

                # Solo alertar si cambió a Down
                if not ok and last_status.get(url) != "down":
                    print(f"[SCHEDULER] Primera caída detectada para {url}")
                    # La alerta ya la envía check_site(url)

                last_status[url] = status_key
            except Exception as e:
                print(f"[SCHEDULER] Error revisando {url}: {e}")

        time.sleep(freq)

if __name__ == "__main__":
    run_monitor()