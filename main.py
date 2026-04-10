import re
from dataclasses import dataclass
from datetime import datetime
import json

LOG_PATTERN = re.compile(
    r'EMIT:\s(?P<date>\S+)\s+(?P<time>\S+)\s+(?P<level>\S+)\s+(?P<event>\S+)\s*(?P<kv>.*)'
)

@dataclass
class AuditEvent:
    timestamp: datetime
    level: str
    event: str
    fields: dict


def parse_kv(kv_string: str):
    fields = {}
    for key_value in re.findall(r'(\w+)=(.*?)(?=\w+=|$)', kv_string):
        fields[key_value[0]] = key_value[1].strip('"')
    return fields


def parse_line(line: str):
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
                    alerts_writer.write(f"{json.dumps({event.event: event.fields})}\n")
                elif event.event in ("RECORD_WARNING"):
                    warnings_writer.write(f"{json.dumps({event.event: event.fields})}\n")
            except Exception as e:
                print(f"Skipping line: {e}")

    return events


if __name__ == "__main__":
    logs = process_log_file("events.log")
    print(f"Processed {len(logs)} events")