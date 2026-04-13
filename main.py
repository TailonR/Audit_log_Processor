import re
from dataclasses import dataclass
from datetime import datetime
import json
import time
from enum import Enum

class ParseError(Enum):
    INVALID_LOG_FORMAT = "INVALID_LOG_FORMAT"
    MALFORMED_TIMESTAMP = "MALFORMED_TIMESTAMP"
    INVALID_KEY_VALUE = "INVALID_KEY_VALUE"

class ParseException(Exception):
    def __init__(self, error_type, message=""):
        super().__init__(message)
        self.error_type = error_type

ERROR_MAP = {
    ParseError.MALFORMED_TIMESTAMP: "parse_fail_timestamp",
    ParseError.INVALID_LOG_FORMAT: "invalid_log_format",
    ParseError.INVALID_KEY_VALUE: "parse_fail_key_value",
}

@dataclass
class AuditEvent:
    timestamp: datetime
    level: str
    event: str
    fields: dict

LOG_PATTERN = re.compile(
    r'(?P<date>\S+)\s+'
    r'(?P<time>\S+)\s+'
    r'(?P<level>INFO|WARN|ERROR|DEBUG)\s+'
    r'(?P<event>[A-Z_]+)\s+'
    r'(?P<kv>.+)'
)

def parse_kv(kv_string):
    fields = {}
    kv_pairs = re.findall(r'(\w+)=(.*?)(?=\s+\w+=|$)', kv_string)

    if not kv_pairs:
        raise ParseException(ParseError.INVALID_KEY_VALUE, "No key-value pairs found")
    
    
    for key_value in kv_pairs:
        if not key_value[0] or not key_value[1]:
            raise ParseException(ParseError.INVALID_KEY_VALUE, f"Invalid key-value pair: {key_value}")
        
        fields[key_value[0].strip()] = key_value[1].strip()
    return fields


def parse_line(line):
    match = LOG_PATTERN.match(line.strip())
    if not match:
        raise ParseException(ParseError.INVALID_LOG_FORMAT, f"Invalid log format: {line}")
    
    data = match.groupdict()

    try:
        timestamp = datetime.strptime(
            f"{data['date']} {data['time']}",
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        raise ParseException(ParseError.MALFORMED_TIMESTAMP, f"Invalid timestamp: {line}")
    
    fields = parse_kv(data["kv"])  # Validate key-value pairs

    return AuditEvent(
        timestamp=timestamp,
        level=data["level"],
        event=data["event"],
        fields=fields
    )

def process_log_file(path):
    events = []
    metrics = {
        "total_lines": 0,
        "parse_success": 0,
        "invalid_log_format": 0,
        "parse_fail_timestamp": 0,
        "parse_fail_key_value": 0
    }

    with open(path) as f, \
         open('alerts_detected.txt', 'w') as alerts_writer, \
         open('warnings_detected.txt', 'w') as warnings_writer, \
         open('log_parse_failures.txt', 'w') as parse_fail_writer:
        for line in f:
            metrics["total_lines"] += 1
            try:
                event = parse_line(line)
                events.append(event)
                metrics["parse_success"] += 1
                # Example: alerting rule
                if event.event in ("LOAD_FAILURE", "AUTH_FAILURE"):
                    alerts_writer.write(f"{json.dumps({event.event: event.fields})}\n")
                elif event.event in ("RECORD_WARNING"):
                    warnings_writer.write(f"{json.dumps({event.event: event.fields})}\n")
            except ParseException as e:
                metrics[ERROR_MAP[e.error_type]] += 1
                parse_fail_writer.write(f"{json.dumps({'error': str(e)})}\n")

    return { "events": events, "diagnostics": metrics }

def write_metrics(metrics):
    with open("metrics.json", "w") as f:
        json.dump(metrics, f)

def run():
    while True:
        logs = process_log_file("event_logs.log")
        write_metrics(logs['diagnostics'])
        time.sleep(60)

if __name__ == "__main__":
    run()