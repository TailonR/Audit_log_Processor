import logging
from logging.handlers import RotatingFileHandler
import random
from datetime import datetime
from enum import Enum
import json
import time

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
    "interval": 1.0
}

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

def get_log_level(level_str):
    return LogLevel[level_str.upper()].value

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
    with open("generator_state.json", "w") as f:
        json.dump({
            "running": True,
            "timestamp": time.time()
        }, f)

def run():
    events = load_events()
    while True:
        log_event(events)
        write_state()
        time.sleep(event_stream["interval"])

if __name__ == "__main__":
    run()