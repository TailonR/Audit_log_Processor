from flask import Flask, jsonify, request
import json
import time
import signal
import os

app = Flask(__name__)

@app.route("/log-status")
def log_status():
    try:
        with open("generator_state.json") as f:
            state = json.load(f)

        state["alive"] = (time.time() - state["timestamp"]) < 5
        return jsonify(state), 200

    except FileNotFoundError:
        return jsonify({"running": False}), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted state file"}), 500
    
@app.route("/analyzer-status")
def analyzer_status():
    try:
        with open("analyzer_state.json") as f:
            state = json.load(f)

        state["alive"] = (time.time() - state["timestamp"]) < 61
        return jsonify(state), 200

    except FileNotFoundError:
        return jsonify({"running": False}), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted state file"}), 500

@app.route("/log-metrics")
def trigger_analysis():
    try:
        with open("metrics.json") as f:
            metrics = json.load(f)
        return jsonify(metrics), 200
    except FileNotFoundError:
        return jsonify({"error": "Metrics file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted metrics file"}), 500

@app.route("/stop-logging")
def stop_logging():
    try:
        with open("generator_state.json") as f:
            state = json.load(f)
            pid = state.get("pid")
            if not pid:
                return jsonify({"error": "No PID found"}), 400

    except FileNotFoundError:
        return jsonify({"error": "No state file"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted state file"}), 500

    try:
        os.kill(pid, signal.SIGTERM)
        return jsonify({"message": f"SIGTERM sent to {pid}"}), 200
    except ProcessLookupError:
        return jsonify({"error": "Process not running"}), 404

@app.route("/stop-analysis")
def stop_analyzer():
    try:
        with open("analyzer_state.json") as f:
            state = json.load(f)
            pid = state.get("pid")
            if not pid:
                return jsonify({"error": "No PID found"}), 400

    except FileNotFoundError:
        return jsonify({"error": "No state file"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted state file"}), 500

    try:
        os.kill(pid, signal.SIGTERM)
        return jsonify({"message": f"SIGTERM sent to {pid}"}), 200
    except ProcessLookupError:
        return jsonify({"error": "Process not running"}), 404