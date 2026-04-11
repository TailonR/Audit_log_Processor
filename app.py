from flask import Flask, jsonify, request
import threading
import time
import random

app = Flask(__name__)

# Shared state
event_stream = {
    "running": False,
    "interval": 1.0,  # seconds
    "thread": None
}

LOG_FILE = "audit_log_sample.log"
EVENT_FILE = "events.log"
LOGS = []

def emit_events():
    ev=open(EVENT_FILE, "w", buffering=1)
    while event_stream["running"]:
        log = random.choice(LOGS)
        print(f"{log}", file=ev, flush=True)
        time.sleep(event_stream["interval"])


@app.route("/start", methods=["POST"])
def start():
    if event_stream["running"]:
        return jsonify({"message": "Already running"}), 400

    interval = request.json.get("interval", 1.0)
    event_stream["interval"] = interval
    event_stream["running"] = True

    thread = threading.Thread(target=emit_events, daemon=True)
    event_stream["thread"] = thread
    thread.start()

    return jsonify({"message": "Event stream started", "interval": interval})


@app.route("/stop", methods=["POST"])
def stop():
    event_stream["running"] = False
    return jsonify({"message": "Event stream stopped"})


@app.route("/status")
def status():
    return jsonify({
        "running": event_stream["running"],
        "interval": event_stream["interval"]
    })


if __name__ == "__main__":
    with open(LOG_FILE, "r") as f:
        for line in f:
            LOGS.append(line.strip())
    app.run(debug=True)