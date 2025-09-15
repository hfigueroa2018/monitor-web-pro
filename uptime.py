import json
import time
from datetime import datetime, timedelta

DB_FILE = "uptime.json"

def load_uptime():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_uptime(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def record_check(url: str, status_ok: bool):
    data = load_uptime()
    if url not in data:
        data[url] = []
    data[url].append({
        "time": datetime.utcnow().isoformat(),
        "status": "up" if status_ok else "down"
    })
    cutoff = datetime.utcnow() - timedelta(hours=24)
    data[url] = [x for x in data[url] if datetime.fromisoformat(x["time"]) > cutoff]
    save_uptime(data)

def uptime_percent(url: str) -> float:
    data = load_uptime()
    if url not in data or not data[url]:
        return 100.0
    total = len(data[url])
    ups = len([x for x in data[url] if x["status"] == "up"])
    return round((ups / total) * 100, 2)

def total_uptime_str(url: str) -> str:
    data = load_uptime()
    if url not in data or not data[url]:
        return "0 min"
    up_secs = 0
    for entry in data[url]:
        if entry["status"] == "up":
            up_secs += 300  # 5 minutos por check
    hours, rem = divmod(up_secs, 3600)
    mins, _ = divmod(rem, 60)
    return f"{hours} hr, {mins} min"