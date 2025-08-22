# src/api/observability.py
from flask import Flask, Response, jsonify
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Counter
import os

app = Flask(__name__)
REGISTRY = CollectorRegistry(auto_describe=True)
REQUESTS = Counter("cog5_requests_total", "Total requests", registry=REGISTRY)

@app.route("/healthz", methods=["GET"])
def healthz():
    # Minimal health checks — extend with dependency checks if needed
    ok = True
    status = {"status": "ok" if ok else "fail"}
    return jsonify(status), 200 if ok else 500

@app.route("/metrics")
def metrics():
    REQUESTS.inc()
    data = generate_latest(REGISTRY)
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    port = int(os.getenv("COG5_METRICS_PORT", 8001))
    app.run(host="0.0.0.0", port=port)