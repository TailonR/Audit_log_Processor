#!/usr/bin/env python3
import re
from dataclasses import dataclass
from datetime import datetime
import json
# Things to do:
# 1) Design a clean internal model.
#     Normalize timestamps (timezone-aware) -- Don't know how to do that since we don't know the orig tz)
#     Enforce valid statuses (SUCCESS, FAILED, etc.)
#     Gracefully handle bad data
# 2) Parse each line into structured data
#     Need to Handle:
#       Missing fields
#       Malformed lines
#       Unexpected formats

LOG_PATTERN = re.compile(
    r'(?P<date>\S+)\s+(?P<time>\S+)\s+(?P<level>\S+)\s+(?P<event>\S+)\s*(?P<kv>.*)'
)

@dataclass
class AuditEvent:
    timestamp: datetime
    level: str
    event: str
    fields: dict


def parse_kv(kv_string: str) -> dict:
    fields = {}
    for key_value in re.findall(r'(\w+)=(.*?)(?=\w+=|$)', kv_string):
        fields[key_value[0]] = key_value[1].strip('"')
    return fields


def parse_line(line: str) -> AuditEvent:
    match = LOG_PATTERN.match(line.strip())
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


    with open(path) as f, open('alerts_detected.txt', 'w') as alerts_writer, open('warnings_detected.txt', 'w') as warnings_writer:
        for line in f:
            try:
                event = parse_line(line)
                events.append(event)

                # Example: alerting rule
                if event.event in ("LOAD_FAILURE", "AUTH_FAILURE"):
                    alerts_writer.write(json.dumps({event.event: event.fields}))
                elif event.event in ("RECORD_WARNING"):
                    warnings_writer.write(json.dumps({event.event: event.fields}))
            except Exception as e:
                print(f"Skipping line: {e}")

    return events


if __name__ == "__main__":
    logs = process_log_file("audit_log_sample.log")
    print(f"Processed {len(logs)} events")