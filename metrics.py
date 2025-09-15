import json
import time
from datetime import datetime, timedelta

DB_METRICS = "metrics.json"

def load_metrics():
    try:
        with open(DB_METRICS, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metrics(data):
    with open(DB_METRICS, "w") as f:
        json.dump(data, f, indent=2)

def record_metric(url: str, status: str, response_time_ms: int):
    data = load_metrics()
    if url not in data:
        data[url] = []
    data[url].append({
        "time": datetime.utcnow().isoformat(),
        "status": status,
        "response_time_ms": response_time_ms
    })
    # Mantener solo último año
    cutoff = datetime.utcnow() - timedelta(days=365)
    data[url] = [x for x in data[url] if datetime.fromisoformat(x["time"]) > cutoff]
    save_metrics(data)

def uptime_range(url: str, days: int) -> float:
    data = load_metrics()
    if url not in data or not data[url]:
        return 100.0
    cutoff = datetime.utcnow() - timedelta(days=days)
    relevant = [x for x in data[url] if datetime.fromisoformat(x["time"]) > cutoff]
    if not relevant:
        return 100.0
    ups = len([x for x in relevant if x["status"] == "up"])
    return round((ups / len(relevant)) * 100, 2)

def incidents_range(url: str, days: int) -> int:
    data = load_metrics()
    if url not in data or not data[url]:
        return 0
    cutoff = datetime.utcnow() - timedelta(days=days)
    relevant = [x for x in data[url] if datetime.fromisoformat(x["time"]) > cutoff]
    downs = 0
    prev = "up"
    for entry in relevant:
        if entry["status"] == "down" and prev == "up":
            downs += 1
        prev = entry["status"]
    return downs

def response_time_stats(url: str, days: int):
    data = load_metrics()
    if url not in data or not data[url]:
        return {"avg": 0, "min": 0, "max": 0}
    cutoff = datetime.utcnow() - timedelta(days=days)
    relevant = [x["response_time_ms"] for x in data[url] if datetime.fromisoformat(x["time"]) > cutoff and x["status"] == "up"]
    if not relevant:
        return {"avg": 0, "min": 0, "max": 0}
    return {
        "avg": round(sum(relevant) / len(relevant), 2),
        "min": min(relevant),
        "max": max(relevant)
    }