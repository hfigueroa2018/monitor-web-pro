from models import db, Metric, Site
from datetime import datetime, timedelta

def record_metric(site, status: str, response_time_ms: int):
    metric = Metric(site_id=site.id, status=status, response_time_ms=response_time_ms)
    db.session.add(metric)
    db.session.commit()
    # Limpiar métricas antiguas (mantener último año)
    cutoff = datetime.utcnow() - timedelta(days=365)
    old_metrics = Metric.query.filter(Metric.time < cutoff).delete()
    db.session.commit()

def uptime_range(site, days: int) -> float:
    cutoff = datetime.utcnow() - timedelta(days=days)
    metrics = Metric.query.filter(Metric.site_id == site.id, Metric.time > cutoff).all()
    if not metrics:
        return 100.0
    ups = len([m for m in metrics if m.status == "up"])
    return round((ups / len(metrics)) * 100, 2)

def incidents_range(site, days: int) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    metrics = Metric.query.filter(Metric.site_id == site.id, Metric.time > cutoff).order_by(Metric.time).all()
    downs = 0
    prev = "up"
    for m in metrics:
        if m.status == "down" and prev == "up":
            downs += 1
        prev = m.status
    return downs

def response_time_stats(site, days: int):
    cutoff = datetime.utcnow() - timedelta(days=days)
    metrics = Metric.query.filter(Metric.site_id == site.id, Metric.time > cutoff, Metric.status == "up", Metric.response_time_ms.isnot(None)).all()
    if not metrics:
        return {"avg": 0, "min": 0, "max": 0}
    times = [m.response_time_ms for m in metrics]
    return {
        "avg": round(sum(times) / len(times), 2),
        "min": min(times),
        "max": max(times)
    }

# Serie temporal de tiempos de respuesta (últimos N minutos)
# Usa None para puntos con estado 'down' para que el gráfico muestre una brecha

def response_time_series(site, minutes: int = 60):
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    metrics = Metric.query.filter(Metric.site_id == site.id, Metric.time > cutoff).order_by(Metric.time).all()
    points = []
    for m in metrics:
        val = m.response_time_ms if m.status == "up" else None
        points.append({
            "time": m.time.isoformat(),
            "value": val,
            "status": m.status
        })
    return points