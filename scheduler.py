# scheduler.py
import time
import json
import os
from monitor import check_site
from database import load_sites

INTERVAL = 60  # segundos (1 minuto)

def run_monitor():
    while True:
        sites = load_sites()
        for site in sites:
            url = site["url"]
            print(f"[SCHEDULER] Revisando {url}")
            check_site(url)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    run_monitor()