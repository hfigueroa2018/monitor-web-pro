from models import Metric
from datetime import datetime, timedelta

def record_check(url: str, status_ok: bool):
    # Now handled by metrics.py
    pass

def uptime_percent(site) -> float:
    cutoff = datetime.utcnow() - timedelta(hours=24)
    metrics = Metric.query.filter(Metric.site_id == site.id, Metric.time > cutoff).all()
    if not metrics:
        return 100.0
    ups = len([m for m in metrics if m.status == "up"])
    return round((ups / len(metrics)) * 100, 2)

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