from flask import Flask, jsonify, request
import json
import time

app = Flask(__name__)

@app.route("/status")
def status():
    try:
        with open("generator_state.json") as f:
            state = json.load(f)

        state["alive"] = (time.time() - state["timestamp"]) < 5
        return state

    except FileNotFoundError:
        return {"running": False}

@app.route("/analyze", methods=["POST"])
def trigger_analysis():
    try:
        with open("metrics.json") as f:
            metrics = json.load(f)
        return jsonify(metrics)
    except FileNotFoundError:
        return jsonify({"error": "Metrics file not found"}), 404