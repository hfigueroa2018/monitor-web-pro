# scheduler.py
import time
import json
from monitor import check_site
from database import load_sites
from notifier import send_alert

CONFIG_FILE = "config.json"


def read_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        # Defaults
        return {
            "freq": int(cfg.get("freq", 60)),
            "action": cfg.get("action", "start"),
        }
    except Exception as e:
        print("[SCHEDULER] Error leyendo config.json:", e)
        return {"freq": 60, "action": "start"}


# Memoria en RAM: último estado por URL
last_status = {}


def run_monitor():
    while True:
        cfg = read_config()
        freq = cfg["freq"]
        action = cfg["action"]

        if action == "stop":
            print("[SCHEDULER] Pausado (action=stop)")
            time.sleep(freq)
            continue

        sites = load_sites()
        for site in sites:
            url = site["url"]
            print(f"[SCHEDULER] Revisando {url}")
            try:
                ok = check_site(url)
                status_key = "up" if ok else "down"

                prev = last_status.get(url)
                # Enviar alerta solo en transición a DOWN
                if status_key == "down" and prev != "down":
                    chats = site.get("chat_ids") or site.get("chat_id")
                    msg = f"❌ {url} está DOWN"
                    print(f"[SCHEDULER] Transición a DOWN, enviando alerta → chats={chats}")
                    send_alert(msg, chats)

                last_status[url] = status_key
            except Exception as e:
                print(f"[SCHEDULER] Error revisando {url}: {e}")

        time.sleep(freq)


if __name__ == "__main__":
    run_monitor()