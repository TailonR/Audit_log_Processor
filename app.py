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
        return jsonify(state), 200

    except FileNotFoundError:
        return jsonify({"running": False}), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted state file"}), 500

@app.route("/analyze", methods=["GET"])
def trigger_analysis():
    try:
        with open("metrics.json") as f:
            metrics = json.load(f)
        return jsonify(metrics), 200
    except FileNotFoundError:
        return jsonify({"error": "Metrics file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted metrics file"}), 500