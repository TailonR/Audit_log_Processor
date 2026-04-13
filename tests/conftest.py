import pytest
import tempfile
import json
from app import app  # adjust import to your Flask app


@pytest.fixture
def client(monkeypatch):
    # Create a temporary directory for all file I/O
    temp_dir = tempfile.TemporaryDirectory()

    # Redirect working directory so file writes stay isolated
    monkeypatch.chdir(temp_dir.name)

    with open("events_sample.json", "w") as f:
      json.dump([
                {"event": "START_PROCESS",
                  "timestamp": "2026-04-09T08:15:23",
                  "level": "INFO",
                  "fields": {
                    "JobID": "78421",
                    "User": "ASCCRLFILOTH",
                    "Host": "server01"
                  }
                },
                {
                  "event": "FILE_RECEIVED",
                  "timestamp": "2026-04-09T08:15:24",
                  "level": "INFO",
                  "fields": {
                    "File": "crdl01in_20260409.dat",
                    "Size": "24576 bytes"
                  }
                }], f)

    # Create Flask test client
    with app.test_client() as client:
        yield client

    # Cleanup
    temp_dir.cleanup()