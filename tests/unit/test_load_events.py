
import json
import pytest
from log_generator import load_events


def test_malformed_events_file(client):
    with open("events_sample.json", "w") as f:
        f.write("NOT JSON")

    with pytest.raises(json.JSONDecodeError):
        load_events()