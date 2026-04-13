import logging
from logging.handlers import RotatingFileHandler
import random
from datetime import datetime
from enum import Enum
import json
import time
import os
import threading
import signal

logging.getLogger('werkzeug').setLevel(logging.WARNING)

LOGGER = logging.getLogger("realtime_logger")
LOGGER.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "event_logs.log",
    maxBytes=10_000_000,
    backupCount=1
)
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)

LOGGER.addHandler(file_handler)
LOGGER.propagate = False

def load_events():
    with open("events_sample.json", "r") as f:
        return json.load(f)
    

event_stream = {
    "running": False,
    "pid": None,
    "timestamp": None
}

stop_event = threading.Event()
def handle_sigterm(signum, frame):
    print("Received SIGTERM, shutting down gracefully...")
    event_stream["running"] = False
    event_stream["timestamp"] = time.time()
    write_state()
    stop_event.set()

signal.signal(signal.SIGTERM, handle_sigterm)

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    ERROR = logging.ERROR

def get_log_level(level_str):
    try:
        return LogLevel[level_str.upper()].value
    except KeyError:
        return logging.INFO

def log_event(events):
    event = random.choice(events)
    log = parse_event(event)
    if event["level"]:
        level = get_log_level(event["level"])
    else:
        level = get_log_level("INFO")
    LOGGER.log(level, log)

def format_timestamp(ts):
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

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

def get_status():
    return {
        "running": event_stream["running"],
        "interval": event_stream["interval"]
    }

def write_state():
  tmp_file = "state.tmp"

  with open(tmp_file, "w") as f:
      json.dump({
            "running": event_stream["running"],
            "pid": event_stream["pid"],
            "timestamp": time.time()
        }, f)

  os.replace(tmp_file, "generator_state.json")

def run():
    event_stream["running"] = True
    event_stream["pid"] = os.getpid()
    events = load_events()
    while not stop_event.is_set():
        log_event(events)
        write_state()
        time.sleep(2)

if __name__ == "__main__":
    run()