# Audit Log Processor

A small Python project that parses generated audit logs, detects alerts and warnings, and exposes basic metrics via an API.

A lightweight, file-based log processing system with a decoupled generator, analyzer, and API layer.

## Features
- Parse and load audit log events from text files
- Detect alerts and warnings and record parse failures
- Simple API for metrics and processing statuses
- Test suite with unit and integration tests

## Architecture

The system consists of three main components:

- **Log Generator (`log_generator.py`)** — produces simulated audit logs
- **Analyzer (`log_analyzer.py`)** — parses logs, detects alerts/warnings, and creates metrics
- **API (`app.py`)** — exposes system state and metrics via HTTP endpoints

The generator and analyzer communicate with the API via shared state files:
- `generator_state.json`
- `analyzer_state.json`

## API Endpoints

### GET /log-status
Returns status of the logger.

Response:
{
  "running": true,
  "alive": true,
  "pid": 37461,
  "timestamp": 1776043339.850122
}

### GET /analyzer-status
Returns status of the log analyzer.

Response:
{
  "running": true,
  "alive": true,
  "pid": 35859,
  "timestamp": 1776042925.129668
}

### GET /log-metrics
Returns aggregated metrics.

Response:
{
  "invalid_log_format": 22,
  "parse_fail_key_value": 0,
  "parse_fail_timestamp": 0,
  "parse_success": 216,
  "total_lines": 238
}

### POST /stop-logging
Gracefully signals the logger to stop

### POST /stop-analysis
Gracefully signals the analyzer to stop

## API Concepts

- `alive` indicates whether a process has updated its heartbeat within the expected time window.

## Metrics

- `invalid_log_format` — lines that do not match expected structure
- `parse_fail_key_value` — malformed key=value pairs
- `parse_fail_timestamp` — invalid timestamps
- `parse_success` — successfully parsed log entries
- `total_lines` — total log lines processed

## Example Log Entry

2026-04-09 08:15:23 INFO START_PROCESS JobID=78421 User=ASCCRLFILOTH Host=server01

## Parsed Output

{
    "event": "START_PROCESS",
    "timestamp": "2026-04-09T08:15:23",
    "level": "INFO",
    "fields": {
      "JobID": "78421",
      "User": "ASCCRLFILOTH",
      "Host": "server01"
    }
}

## Installation

1. Create a Python 3.10+ virtual environment:

   python3 -m venv .venv
   source .venv/bin/activate

2. Install dependencies:

   pip install -r requirements.txt

# Running the System (Local Dev)

## Terminal 1 – Start log generator
```bash
python3 log_generator.py
```

## Terminal 2 – Start analyzer
```bash
python3 log_analyzer.py
```

## Terminal 3 – Start API
```bash
gunicorn app:app
```

## Tests

Run the test suite with pytest:

```bash
pytest
```

The repository includes both unit tests and integration tests under `tests/`.

## Project Layout

- `app.py` — API entrypoint
- `log_analyzer.py` — main processing orchestration
- `log_generator.py` — test log generator
- `tests/` — unit and integration tests
- 
### State & Data Files
- `events_sample.json` — seed data for log generation
- `generator_state.json` — logger process state
- `analyzer_state.json` — analyzer process state
- `metrics.json` — aggregated metrics output
- `alerts_detected.txt` - the alerts emitted by the analyzer
- `warnings_detected.txt` - the warnings emitted by the analyzer

## Design Decisions

- **File-based state** instead of a database for simplicity and portability
- **Loose coupling** between generator, processor, and API
- **Graceful failure handling** for malformed logs
- **Log format fixed** as date, time, log level, event, fields. All are required
- **Event seed file** so the generator can have something to log

## Assumptions

- Single-instance execution (no concurrent writers to state files)
- Local file system is reliable for state persistence
- Valid entries for log level are from the `events_sample.json` seed file

## Error Handling

- Malformed logs are recorded as parse failures
- Corrupted state files return HTTP 500
- Missing state files default to "not running"

## Future Improvements

- Replace file-based state with Redis or a database
- Containerize with Docker

## Contributing

Feel free to open issues or PRs. Keep changes small and include tests for new behavior.

## License

See the `LICENSE` file in the repository.
