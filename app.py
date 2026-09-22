"""Building Energy Performance Analytics – local Flask dashboard."""
from __future__ import annotations

from flask import Flask, jsonify, render_template
from pipeline import AnalyticsPipeline


app = Flask(__name__)
pipeline = AnalyticsPipeline("energy_analytics.db")


@app.before_request
def ensure_data() -> None:
    pipeline.bootstrap()


@app.get("/")
def dashboard():
    return render_template("dashboard.html", report=pipeline.report())


@app.get("/api/report")
def report_api():
    return jsonify(pipeline.report())


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
