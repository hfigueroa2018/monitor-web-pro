from flask import Flask, request, jsonify
from metrics import uptime_range, incidents_range, response_time_stats

app = Flask(__name__)

@app.route("/metrics/<path:url>")
def metrics_data(url):
    from urllib.parse import unquote
    url = unquote(url)
    days = int(request.args.get("days", 1))
    return jsonify({
        "uptime": uptime_range(url, days),
        "incidents": incidents_range(url, days),
        "response": response_time_stats(url, days)
    })