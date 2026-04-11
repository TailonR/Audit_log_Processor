from flask import Flask, jsonify, request
import threading
import time
import random
import logging
import json
from datetime import datetime

logging.getLogger('werkzeug').setLevel(logging.WARNING)

LOGGER = logging.getLogger("realtime_logger")
LOGGER.setLevel(logging.INFO)

file_handler = logging.FileHandler("event_logs.log")
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)

LOGGER.addHandler(file_handler)

LOGGER.propagate = False

app = Flask(__name__)

EVENT_FILE = "events_sample.json"
EVENTS = []

# Shared state
event_stream = {
    "running": False,
    "interval": 1.0,  # seconds
    "thread": None
}

def log_event():
    while event_stream["running"]:
        event = random.choice(EVENTS)
        log = parse_event(event)
        LOGGER.info(log)

def format_timestamp(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def format_fields(fields):
    fields_string = ""
    for k,v in fields.items():
        fields_string += f" {k}={v}"
    return fields_string

def parse_event(event):
    required = ["event", "timestamp", "level", "fields"]
    if all(event.get(k) is None for k in required[:3]) and event.get("fields") == {} :
        return "??????? ??????? ???????"
    
    return f"{format_timestamp(event['timestamp'])} {event['level']} {event['event']}{format_fields(event['fields'])}"

@app.route("/start", methods=["POST"])
def start():
    if event_stream["running"]:
        return jsonify({"message": "Already running"}), 400

    interval = request.json.get("interval", 1.0)
    event_stream["interval"] = interval
    event_stream["running"] = True

    thread = threading.Thread(target=log_event, daemon=True)
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
    with open(EVENT_FILE, "r") as f:
        EVENTS = json.load(f)

    app.run(debug=True)