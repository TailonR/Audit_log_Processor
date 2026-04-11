import re
from dataclasses import dataclass
from datetime import datetime
import json
from datetime import datetime

class ParseError:
    OK = "OK"
    CORRUPTED_LINE = "CORRUPTED_LINE"
    MALFORMED_TIMESTAMP = "MALFORMED_TIMESTAMP"
    MISSING_FIELDS = "MISSING_FIELDS"
    INVALID_KEY_VALUE = "INVALID_KEY_VALUE"

@dataclass
class AuditEvent:
    timestamp: datetime
    level: str
    event: str
    fields: dict

def validate_line(line: str):
    line = line.strip()
    # 1. basic sanity
    if not line or "????" in line:
        return {
            "result": ParseError.CORRUPTED_LINE,
            "raw": line
        }

    parts = line.split(maxsplit=4)
    if len(parts) < 5:
        return {
            "result": ParseError.MISSING_FIELDS,
            "raw": line
        }

    date, time, _, _ = parts[:4]
    rest = parts[4]

    # 2. timestamp validation (try formats)
    if not is_valid_timestamp(date, time):
        return {
            "result": ParseError.MALFORMED_TIMESTAMP,
            "raw": line
        }

    # 3. key=value validation (if present)
    pattern = r'(\w+)=(.*?)(?=\w+=|$)'
    if re.fullmatch(pattern, ''.join(rest)) is None:
        return {
            "result": ParseError.INVALID_KEY_VALUE,
            "raw": line
        }

    return { "result": ParseError.OK }

def is_valid_timestamp(date, time):
    try:
        datetime.strptime(
            f"{date} {time}",
            "%Y-%m-%d %H:%M:%S"
        )
        return True
    except ValueError:
        return False

def parse_kv(kv_string: str):
    fields = {}
    for key_value in re.findall(r'(\w+)=(.*?)(?=\w+=|$)', kv_string):
        fields[key_value[0].strip()] = key_value[1].strip()
    return fields


def parse_line(line: str):
    pattern=re.compile(r'(?P<date>\S+)\s+(?P<time>\S+)\s+(?P<level>\S+)\s+(?P<event>\S+)\s*(?P<kv>.*)')

    match = pattern.match(line.strip())
    if not match:
        raise ValueError(f"Invalid log format: {line}")
    
    data = match.groupdict()

    timestamp = datetime.strptime(
        f"{data['date']} {data['time']}",
        "%Y-%m-%d %H:%M:%S"
    )

    return AuditEvent(
        timestamp=timestamp,
        level=data["level"],
        event=data["event"],
        fields=parse_kv(data["kv"])
    )

def process_log_file(path: str):
    events = []
    metrics = {
        "total_lines": 0,
        "parse_success": 0,
        "parse_fail_timestamp": 0,
        "parse_fail_corrupted_line": 0,
        "parse_fail_missing_fields": 0,
        "parse_fail_key_value": 0
    }

    with open(path) as f, \
         open('alerts_detected.txt', 'w') as alerts_writer, \
         open('warnings_detected.txt', 'w') as warnings_writer, \
         open('log_parse_failures.txt', 'w') as parse_fail_writer:
        for line in f:
            metrics["total_lines"] += 1
            validation = validate_line(line)
            if validation["result"] == ParseError.OK:
                metrics["parse_success"] += 1
                event = parse_line(line)
                events.append(event)

                # Example: alerting rule
                if event.event in ("LOAD_FAILURE", "AUTH_FAILURE"):
                    alerts_writer.write(f"{json.dumps({event.event: event.fields})}\n")
                elif event.event in ("RECORD_WARNING"):
                    warnings_writer.write(f"{json.dumps({event.event: event.fields})}\n")
            else:
                if validation["result"] == ParseError.MALFORMED_TIMESTAMP:
                    metrics["parse_fail_timestamp"] += 1
                elif validation["result"] == ParseError.CORRUPTED_LINE:
                    metrics["parse_fail_corrupted_line"] += 1
                elif validation["result"] == ParseError.MISSING_FIELDS:
                    metrics["parse_fail_missing_fields"] += 1
                elif validation["result"] == ParseError.INVALID_KEY_VALUE:
                    metrics["parse_fail_key_value"] += 1
                parse_fail_writer.write(f"{json.dumps(validation)}\n")

    return { "events": events, "diagnostics": metrics }


if __name__ == "__main__":
    logs = process_log_file("events.log")
    print(f"Metrics: {logs['diagnostics']}")