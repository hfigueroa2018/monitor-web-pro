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

# Bandera para indicar si es la primera vez que se revisa un sitio
first_check = {}

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

                # Alertar si cambió a Down o si es la primera vez que se detecta caída
                if not ok and (last_status.get(url) != "down" or first_check.get(url) == True):
                    print(f"[SCHEDULER] Estado Down detectado para {url}")
                    # La alerta ya la envía check_site(url)
                    first_check[url] = False

                last_status[url] = status_key
                # Marcar como revisado al menos una vez
                if url not in first_check:
                    first_check[url] = True
            except Exception as e:
                print(f"[SCHEDULER] Error revisando {url}: {e}")

        time.sleep(freq)

if __name__ == "__main__":
    run_monitor()